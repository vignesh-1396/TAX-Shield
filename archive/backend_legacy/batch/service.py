"""
TaxPay Guard - Batch Processing Service
Core business logic for batch vendor compliance checking
"""
import os
import uuid
import zipfile
import tempfile
from datetime import datetime
from typing import Dict, List

# Import from parent directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    create_batch_job, add_batch_items, get_batch_job, get_batch_items,
    update_batch_job_status, update_batch_job_progress, update_batch_item,
    set_batch_output_file, save_compliance_check
)
from gsp_client import MockGSPProvider
from decision_engine import check_vendor
from pdf_generator import generate_certificate


# Output directory for batch files
BATCH_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "batches")
os.makedirs(BATCH_OUTPUT_DIR, exist_ok=True)


def create_batch(items: List[Dict], input_filename: str) -> Dict:
    """
    Create a new batch job from parsed CSV items.
    
    Args:
        items: List of dicts with gstin, vendor_name, amount
        input_filename: Original uploaded filename
        
    Returns:
        Dict with job_id and status
    """
    job_id = str(uuid.uuid4())
    
    # Create batch job record
    create_batch_job(job_id, len(items), input_filename)
    
    # Add all items to batch
    add_batch_items(job_id, items)
    
    return {
        "job_id": job_id,
        "total_vendors": len(items),
        "status": "PENDING",
        "message": "Batch job created. Processing will begin shortly."
    }


def process_batch_sync(job_id: str) -> Dict:
    """
    Process a batch job synchronously (for MVP/small batches).
    For production, use Celery async version.
    
    Args:
        job_id: Batch job ID
        
    Returns:
        Dict with final status
    """
    job = get_batch_job(job_id)
    if not job:
        return {"error": "Job not found"}
    
    # Update status to processing
    update_batch_job_status(job_id, "PROCESSING")
    
    items = get_batch_items(job_id, status="PENDING")
    processed = 0
    success = 0
    failed = 0
    
    # Create temp directory for certificates
    batch_dir = os.path.join(BATCH_OUTPUT_DIR, job_id)
    certs_dir = os.path.join(batch_dir, "certificates")
    os.makedirs(certs_dir, exist_ok=True)
    
    for item in items:
        try:
            # 1. Get vendor data from GSP (or cache)
            vendor_data = MockGSPProvider.get_vendor_data(item['gstin'])
            
            # 2. Run decision engine
            decision_result = check_vendor(vendor_data)
            
            # 3. Save compliance check to database
            check_id = save_compliance_check(
                gstin=item['gstin'],
                vendor_name=vendor_data.get('legal_name', item.get('vendor_name', '')),
                amount=item.get('amount', 0),
                decision=decision_result['decision'],
                rule_id=decision_result['rule_id'],
                reason=decision_result['reason'],
                risk_level=decision_result['risk_level'],
                data_source="BATCH"
            )
            
            # 4. Generate certificate PDF
            cert_data = {
                **decision_result,
                "gstin": item['gstin'],
                "vendor_name": vendor_data.get('legal_name', item.get('vendor_name', '')),
                "amount": item.get('amount', 0),
                "check_id": check_id,
                "gst_status": vendor_data.get('gst_status', 'Unknown'),
                "filing_history": vendor_data.get('filing_history', []),
            }
            
            pdf_bytes = generate_certificate(cert_data)
            
            # Save certificate
            safe_name = item['gstin'].replace('/', '_')
            cert_filename = f"{safe_name}_{decision_result['decision']}.pdf"
            cert_path = os.path.join(certs_dir, cert_filename)
            
            with open(cert_path, 'wb') as f:
                f.write(pdf_bytes)
            
            # 5. Update item status
            update_batch_item(
                item_id=item['id'],
                status="SUCCESS",
                decision=decision_result['decision'],
                check_id=check_id
            )
            
            success += 1
            
        except Exception as e:
            update_batch_item(
                item_id=item['id'],
                status="FAILED",
                error_message=str(e)
            )
            failed += 1
        
        processed += 1
        update_batch_job_progress(job_id, processed, success, failed)
    
    # Create ZIP file
    zip_filename = f"TaxPayGuard_Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(batch_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all certificates
        for cert_file in os.listdir(certs_dir):
            cert_path = os.path.join(certs_dir, cert_file)
            zipf.write(cert_path, f"certificates/{cert_file}")
        
        # Add summary report (simple text for now)
        summary = f"""TaxPay Guard - Batch Processing Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Vendors: {processed}
Successful: {success}
Failed: {failed}

Job ID: {job_id}
"""
        zipf.writestr("summary.txt", summary)
    
    # Update job as completed
    set_batch_output_file(job_id, zip_path)
    update_batch_job_status(job_id, "COMPLETED")
    
    return {
        "job_id": job_id,
        "status": "COMPLETED",
        "total": processed,
        "success": success,
        "failed": failed,
        "output_file": zip_path
    }


def get_batch_status(job_id: str) -> Dict:
    """Get current status of a batch job"""
    job = get_batch_job(job_id)
    if not job:
        return None
    
    progress_percent = 0
    if job['total_count'] > 0:
        progress_percent = round((job['processed_count'] / job['total_count']) * 100, 1)
    
    return {
        "job_id": job_id,
        "status": job['status'],
        "total": job['total_count'],
        "processed": job['processed_count'],
        "success": job['success_count'],
        "failed": job['failed_count'],
        "progress_percent": progress_percent,
        "output_file": job.get('output_filename'),
        "created_at": job['created_at'],
        "completed_at": job.get('completed_at')
    }
