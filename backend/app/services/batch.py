import os
import uuid
import zipfile
from datetime import datetime
from typing import Dict, List
from app.core.config import settings
from app.db.crud import batch as batch_crud
from app.db.crud import check as check_crud
from app.db.crud.vendor import save_vendor, get_cached_vendor  # Import vendor CRUD
from app.services.gsp import get_gsp_provider
from app.services.decision import DecisionEngine
from app.services.pdf import generate_certificate

# Configuration
BATCH_OUTPUT_DIR = settings.BATCH_OUTPUT_DIR
os.makedirs(BATCH_OUTPUT_DIR, exist_ok=True)

engine = DecisionEngine()

def create_batch(items: List[Dict], input_filename: str, user_id: str = None) -> Dict:
    """Create a new batch job from parsed CSV items."""
    job_id = str(uuid.uuid4())
    batch_crud.create_batch_job(job_id, len(items), input_filename)
    batch_crud.add_batch_items(job_id, items)
    
    return {
        "job_id": job_id,
        "total_vendors": len(items),
        "status": "PENDING",
        "message": "Batch job created. Processing will begin shortly."
    }

def process_batch_sync(job_id: str) -> Dict:
    """Process a batch job synchronously (for small batches)."""
    job = batch_crud.get_batch_job(job_id)
    if not job:
        return {"error": "Job not found"}
    
    batch_crud.update_batch_job_status(job_id, "PROCESSING")
    items = batch_crud.get_batch_items(job_id, status="PENDING")
    
    processed = 0
    success = 0
    failed = 0
    
    # Create temp directory for certificates
    batch_dir = os.path.join(BATCH_OUTPUT_DIR, job_id)
    certs_dir = os.path.join(batch_dir, "certificates")
    os.makedirs(certs_dir, exist_ok=True)
    
    # MAXIMUM PERFORMANCE: Parallel processing with high concurrency
    # Target: 500 vendors in ~30 seconds = ~16 vendors/second
    # Using 30 workers to maximize throughput
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import logging
    
    logger = logging.getLogger(__name__)
    max_workers = min(30, len(items))  # Up to 30 parallel workers
    
    # Instantiate provider once for the entire batch to reuse token
    provider = get_gsp_provider()
    
    logger.info(f"Starting parallel batch processing with {max_workers} workers")
    
    def process_single_vendor(item: Dict) -> Dict:
        """Process a single vendor (thread-safe)"""
        try:
            # Reuse the same provider instance (uses cached token)
            vendor_data = provider.get_vendor_data(item['gstin'])
            
            if not vendor_data:
                raise Exception("Failed to fetch vendor data from GSP")

            # OPTIMIZATION: Save vendor data to DB for on-demand PDF generation later
            save_vendor(vendor_data)

            decision_result = engine.check_vendor(vendor_data)
            
            check_id = check_crud.save_compliance_check(
                gstin=item['gstin'],
                vendor_name=vendor_data.get('legal_name', item.get('vendor_name', '')),
                amount=item.get('amount', 0),
                decision=decision_result['decision'],
                rule_id=decision_result['rule_id'],
                reason=decision_result['reason'],
                risk_level=decision_result['risk_level'],
                data_source="BATCH"
            )

            # OPTIMIZATION: Skip PDF generation for now (On-Demand)
            # PDF will be generated only when user requests download
            
            batch_crud.update_batch_item(
                item_id=item['id'],
                status="SUCCESS",
                decision=decision_result['decision'],
                check_id=check_id,
                risk_level=decision_result['risk_level'],
                reason=decision_result['reason']
            )
            
            return {'status': 'SUCCESS', 'item_id': item['id']}
            
        except Exception as e:
            batch_crud.update_batch_item(
                item_id=item['id'],
                status="FAILED",
                error_message=str(e)
            )
            return {'status': 'FAILED', 'item_id': item['id'], 'error': str(e)}
    
    # Process vendors in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_item = {
            executor.submit(process_single_vendor, item): item 
            for item in items
        }
        
        # Process results as they complete
        for future in as_completed(future_to_item):
            result = future.result()
            
            if result['status'] == 'SUCCESS':
                success += 1
            else:
                failed += 1
            
            processed += 1
            
            # Update progress every 10 items or on completion
            if processed % 10 == 0 or processed == len(items):
                batch_crud.update_batch_job_progress(job_id, processed, success, failed)
                logger.info(f"Batch {job_id}: {processed}/{len(items)} processed ({success} success, {failed} failed)")
    
    # Generate Results CSV
    import csv
    results_csv_path = os.path.join(batch_dir, "results.csv")
    
    # Get all batch items with results
    all_items = batch_crud.get_batch_items(job_id, status=None)  # Get all items regardless of status
    
    with open(results_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['gstin', 'party_name', 'amount', 'status', 'decision', 'risk_level', 'reason']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in all_items:
            writer.writerow({
                'gstin': item.get('gstin', ''),
                'party_name': item.get('vendor_name', ''),
                'amount': item.get('amount', 0),
                'status': 'SUCCESS' if item.get('status') == 'SUCCESS' else 'FAILED',
                'decision': item.get('decision', 'N/A'),
                'risk_level': item.get('risk_level', 'N/A'),
                'reason': item.get('error_message', '') if item.get('status') == 'FAILED' else item.get('reason', 'N/A')
            })
    
    # Create ZIP
    zip_filename = f"TaxPayGuard_Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(batch_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add results CSV
        zipf.write(results_csv_path, "results.csv")
        
        # Add certificates
        for cert_file in os.listdir(certs_dir):
            cp = os.path.join(certs_dir, cert_file)
            zipf.write(cp, f"certificates/{cert_file}")
        
        summary = f"Total: {processed}\nSuccess: {success}\nFailed: {failed}\nJob ID: {job_id}"
        zipf.writestr("summary.txt", summary)
    
    batch_crud.set_batch_output_file(job_id, zip_path)
    batch_crud.update_batch_job_status(job_id, "COMPLETED")
    
    return {
        "job_id": job_id,
        "status": "COMPLETED",
        "total": processed,
        "success": success,
        "failed": failed,
        "output_file": zip_path
    }

def get_batch_status(job_id: str) -> Dict:
    """Get current status of a batch job."""
    job = batch_crud.get_batch_job(job_id)
    if not job:
        return None
    
    progress = 0
    if job['total_count'] > 0:
        progress = round((job['processed_count'] / job['total_count']) * 100, 1)
    
    return {
        "job_id": job_id,
        "status": job['status'],
        "total": job['total_count'],
        "processed": job['processed_count'],
        "success": job['success_count'],
        "failed": job['failed_count'],
        "progress_percent": progress,
        "output_file": job.get('output_filename'),
        "created_at": str(job['created_at']),
        "completed_at": str(job.get('completed_at', ''))
    }

def generate_certificates_zip(job_id: str) -> str:
    """
    On-Demand PDF Generation:
    Generates missing certificates and updates/recreates the ZIP file.
    Returns the path to the updated ZIP file.
    """
    # Get items
    items = batch_crud.get_batch_items(job_id, status="SUCCESS")
    if not items:
        job = batch_crud.get_batch_job(job_id)
        return job.get('output_filename') if job else None
        
    batch_dir = os.path.join(BATCH_OUTPUT_DIR, job_id)
    certs_dir = os.path.join(batch_dir, "certificates")
    os.makedirs(certs_dir, exist_ok=True)
    
    # Check if certificates already exist
    existing_certs = set(os.listdir(certs_dir))
    items_to_generate = [
        item for item in items 
        if not any(f"{item['gstin'].replace('/', '_')}" in f for f in existing_certs)
    ]
    
    if items_to_generate:
        from app.db.crud.vendor import get_cached_vendor
        from concurrent.futures import ThreadPoolExecutor
        
        # Helper for parallel generation
        def generate_single_pdf(item):
            try:
                # Get cached vendor data
                vendor_data = get_cached_vendor(item['gstin'])
                if not vendor_data:
                    return False
                    
                cert_data = {
                    "decision": item.get('decision'),
                    "rule_id": "BATCH_RULE", 
                    "reason": item.get('reason'),
                    "risk_level": item.get('risk_level'),
                    "gstin": item['gstin'],
                    "vendor_name": item.get('vendor_name'),
                    "amount": item.get('amount'),
                    "check_id": item.get('check_id'),
                    "gst_status": vendor_data.get('gst_status', 'Unknown'),
                    "filing_history": vendor_data.get('filing_history', []),
                }
                
                pdf_bytes = generate_certificate(cert_data)
                safe_name = item['gstin'].replace('/', '_')
                cert_filename = f"{safe_name}_{item.get('decision')}.pdf"
                cert_path = os.path.join(certs_dir, cert_filename)
                
                with open(cert_path, 'wb') as f:
                    f.write(pdf_bytes)
                return True
            except Exception:
                return False

        # Generate in parallel
        max_workers = min(30, len(items_to_generate))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(generate_single_pdf, items_to_generate))
            
    # Re-create ZIP with certificates
    job = batch_crud.get_batch_job(job_id)
    current_zip_path = job.get('output_filename')
    results_csv_path = os.path.join(batch_dir, "results.csv")
    
    # Needs a new name if we are adding content? Or overwrite?
    # Overwriting is safer for valid file handling
    if not current_zip_path or not os.path.exists(current_zip_path):
        current_zip_path = os.path.join(batch_dir, f"TaxPayGuard_Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")

    # Update/Create ZIP
    with zipfile.ZipFile(current_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(results_csv_path):
            zipf.write(results_csv_path, "results.csv")
            
        zipf.writestr("summary.txt", f"Full Report with Certificates\nJob ID: {job_id}")
        
        for cert_file in os.listdir(certs_dir):
            cp = os.path.join(certs_dir, cert_file)
            zipf.write(cp, f"certificates/{cert_file}")
            
    # Update job with new file path if changed (or just to be safe)
    batch_crud.set_batch_output_file(job_id, current_zip_path)
    
    return current_zip_path
