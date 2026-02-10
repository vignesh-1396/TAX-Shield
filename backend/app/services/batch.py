import os
import uuid
import zipfile
from datetime import datetime
from typing import Dict, List
from app.core.config import settings
from app.db.crud import batch as batch_crud
from app.db.crud import check as check_crud
from app.services.gsp import MockGSPProvider
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
    
    for item in items:
        try:
            vendor_data = MockGSPProvider.get_vendor_data(item['gstin'])
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
            safe_name = item['gstin'].replace('/', '_')
            cert_filename = f"{safe_name}_{decision_result['decision']}.pdf"
            cert_path = os.path.join(certs_dir, cert_filename)
            
            with open(cert_path, 'wb') as f:
                f.write(pdf_bytes)
            
            batch_crud.update_batch_item(
                item_id=item['id'],
                status="SUCCESS",
                decision=decision_result['decision'],
                check_id=check_id
            )
            success += 1
            
        except Exception as e:
            batch_crud.update_batch_item(
                item_id=item['id'],
                status="FAILED",
                error_message=str(e)
            )
            failed += 1
        
        processed += 1
        batch_crud.update_batch_job_progress(job_id, processed, success, failed)
    
    # Create ZIP
    zip_filename = f"TaxPayGuard_Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(batch_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
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
