"""
Celery Tasks for Async Batch Processing
"""
from celery import group, chord
from celery.result import AsyncResult
from typing import List, Dict
import logging
from datetime import datetime

from app.core.celery_app import celery_app
from app.services.gsp import get_gsp_provider
from app.services.decision import DecisionEngine
from app.services.pdf import generate_certificate
from app.services.storage import storage
from app.db.crud import batch as batch_crud
from app.db.crud import check as check_crud
from app.db.crud import vendor as vendor_crud
import os
import zipfile

logger = logging.getLogger(__name__)
engine = DecisionEngine()


@celery_app.task(bind=True, max_retries=3)
def process_single_vendor_task(self, item: Dict, job_id: str) -> Dict:
    """
    Process a single vendor asynchronously
    
    Args:
        item: Vendor data from CSV
        job_id: Batch job ID
    
    Returns:
        Processing result
    """
    try:
        gstin = item.get("gstin", "").strip().upper()
        amount = float(item.get("amount", 0))
        party_name = item.get("party_name", "")
        
        # Fetch vendor data
        vendor_data = vendor_crud.get_cached_vendor(gstin, max_age_hours=24)
        if not vendor_data:
            provider = get_gsp_provider()
            vendor_data = provider.get_vendor_data(gstin)
            if vendor_data:
                vendor_crud.save_vendor(vendor_data)
        
        # Run decision engine
        result = engine.check_vendor(vendor_data, amount)
        
        # Save compliance check
        check_id = check_crud.save_compliance_check(
            gstin=gstin,
            vendor_name=vendor_data.get("legal_name", party_name) if vendor_data else party_name,
            amount=amount,
            decision=result["decision"],
            rule_id=result["rule_id"],
            reason=result["reason"],
            risk_level=result["risk_level"],
            data_source="GSP_LIVE" if vendor_data else "UNKNOWN"
        )
        
        # Update batch item status
        batch_crud.update_batch_item_status(
            job_id=job_id,
            gstin=gstin,
            status="COMPLETED",
            decision=result["decision"],
            check_id=check_id
        )
        
        return {
            "gstin": gstin,
            "status": "success",
            "decision": result["decision"],
            "check_id": check_id
        }
        
    except Exception as e:
        logger.error(f"Error processing vendor {item.get('gstin')}: {e}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=5 ** self.request.retries)
        
        # Mark as failed after max retries
        batch_crud.update_batch_item_status(
            job_id=job_id,
            gstin=item.get("gstin", ""),
            status="FAILED",
            decision="ERROR",
            check_id=None
        )
        
        return {
            "gstin": item.get("gstin"),
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def generate_batch_output_task(job_id: str, results: List[Dict]) -> Dict:
    """
    Generate final batch output (CSV + ZIP) after all vendors processed
    
    Args:
        job_id: Batch job ID
        results: List of processing results
    
    Returns:
        Output file information
    """
    try:
        logger.info(f"Generating batch output for job {job_id}")
        
        # Get all batch items
        items = batch_crud.get_batch_items(job_id)
        
        # Create output directory
        batch_dir = os.path.join("batch_outputs", job_id)
        certs_dir = os.path.join(batch_dir, "certificates")
        os.makedirs(certs_dir, exist_ok=True)
        
        # Generate CSV
        csv_path = os.path.join(batch_dir, f"batch_results_{job_id}.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("GSTIN,Party Name,Amount,Decision,Risk Level,Rule ID,Reason,Certificate\n")
            
            for item in items:
                cert_file = ""
                if item.get("check_id"):
                    # Generate PDF certificate
                    check = check_crud.get_check_by_id(item["check_id"])
                    if check:
                        vendor_data = vendor_crud.get_cached_vendor(item["gstin"])
                        check_data = {
                            **check,
                            "filing_history": vendor_data.get("filing_history", []) if vendor_data else [],
                            "registration_date": vendor_data.get("registration_date", "") if vendor_data else "",
                            "gst_status": vendor_data.get("gst_status", "") if vendor_data else "",
                        }
                        
                        pdf_bytes = generate_certificate(check_data)
                        cert_filename = f"cert_{item['gstin']}_{item['check_id']}.pdf"
                        cert_path = os.path.join(certs_dir, cert_filename)
                        
                        with open(cert_path, 'wb') as pdf_file:
                            pdf_file.write(pdf_bytes)
                        
                        cert_file = f"certificates/{cert_filename}"
                
                f.write(f"{item['gstin']},{item.get('party_name', '')},{item.get('amount', 0)},"
                       f"{item.get('decision', 'PENDING')},{item.get('risk_level', 'UNKNOWN')},"
                       f"{item.get('rule_id', '')},{item.get('reason', '')},{cert_file}\n")
        
        # Create ZIP file
        zip_path = os.path.join(batch_dir, f"batch_result_{job_id}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(csv_path, os.path.basename(csv_path))
            for root, dirs, files in os.walk(certs_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, batch_dir)
                    zipf.write(file_path, arcname)
        
        # Upload to storage
        storage_key = f"batches/{job_id}/batch_result_{job_id}.zip"
        storage_url = storage.upload_file(zip_path, storage_key)
        
        # Update batch job
        batch_crud.update_batch_job_status(
            job_id=job_id,
            status="COMPLETED",
            output_file=storage_url
        )
        
        logger.info(f"Batch output generated: {storage_url}")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "output_file": storage_url,
            "total_processed": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error generating batch output: {e}")
        batch_crud.update_batch_job_status(job_id=job_id, status="FAILED")
        raise


@celery_app.task(bind=True)
def process_batch_async(self, job_id: str, items: List[Dict]) -> Dict:
    """
    Process entire batch asynchronously with parallel execution
    
    Args:
        job_id: Batch job ID
        items: List of vendor items from CSV
    
    Returns:
        Processing summary
    """
    try:
        logger.info(f"Starting async batch processing for job {job_id} with {len(items)} items")
        
        # Update job status
        batch_crud.update_batch_job_status(job_id, "PROCESSING")
        
        # Create parallel tasks for each vendor
        job = group(
            process_single_vendor_task.s(item, job_id)
            for item in items
        )
        
        # Execute with callback to generate output
        callback = generate_batch_output_task.s(job_id)
        result = chord(job)(callback)
        
        # Update progress
        total = len(items)
        for idx in range(total):
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': idx + 1,
                    'total': total,
                    'percent': int((idx + 1) / total * 100),
                    'status': 'processing'
                }
            )
        
        return {
            "job_id": job_id,
            "status": "processing",
            "total_items": len(items),
            "message": "Batch processing in progress"
        }
        
    except Exception as e:
        logger.error(f"Batch processing failed for job {job_id}: {e}")
        batch_crud.update_batch_job_status(job_id, "FAILED")
        raise


@celery_app.task
def cleanup_old_batches():
    """
    Periodic task to cleanup old batch files
    Run daily via Celery beat
    """
    try:
        logger.info("Running batch cleanup task")
        storage.cleanup_old_files(days=7)
        logger.info("Batch cleanup completed")
    except Exception as e:
        logger.error(f"Batch cleanup failed: {e}")
