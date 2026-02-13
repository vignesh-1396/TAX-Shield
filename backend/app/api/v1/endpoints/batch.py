from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import logging

from app.services import batch as batch_service
from app.utils.csv_parser import parse_csv_content, generate_sample_csv
from app.api.deps import get_current_user
from app.services.storage import storage

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VENDORS_PER_BATCH = 500

@router.post("/upload")
async def upload_batch(
    file: UploadFile = File(...),
    current_user: dict = None  # Made optional for MVP
):
    """
    Upload a CSV for batch processing - Now async!
    Returns immediately with job_id for status polling
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    content = await file.read()
    items, errors = parse_csv_content(content)
    
    if not items:
        raise HTTPException(status_code=400, detail={"message": "No valid vendors found", "errors": errors[:10]})
    
    if len(items) > MAX_VENDORS_PER_BATCH:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_VENDORS_PER_BATCH} vendors allowed")
    
    # Create batch job
    result = batch_service.create_batch(items, file.filename, user_id=current_user.get("id") if current_user else None)
    job_id = result['job_id']
    
    # Process batch synchronously (optimized - takes 5-10 seconds)
    logger.info(f"Starting synchronous batch processing for job {job_id} - {len(items)} vendors")
    try:
        batch_service.process_batch_sync(job_id)
        logger.info(f"Batch processing completed for job {job_id}")
        
        # Get final status
        final_status = batch_service.get_batch_status(job_id)
        
        return {
            "job_id": job_id,
            "total": len(items), # Fix for frontend which expects 'total'
            "total_vendors": len(items),
            "status": final_status.get('status', 'COMPLETED'),
            "processed": final_status.get('processed', len(items)),
            "success": final_status.get('success', 0),
            "failed": final_status.get('failed', 0),
            "message": f"Batch processed successfully - {final_status.get('success', 0)} succeeded, {final_status.get('failed', 0)} failed",
            "parse_errors": errors[:5] if errors else []
        }
    except Exception as e:
        logger.error(f"Batch processing failed for job {job_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@router.get("/status/{job_id}")
async def get_job_status(job_id: str, current_user: dict = None):
    """
    Get batch job status with real-time progress
    """
    # Get job from database
    status = batch_service.get_batch_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get Celery task status if processing
    if status['status'] == 'PROCESSING':
        # Try to get task progress
        try:
            # Note: We'd need to store task_id in DB to retrieve it here
            # For now, return DB status
            pass
        except Exception as e:
            logger.warning(f"Could not get task status: {e}")
    
    return status

@router.get("/download/{job_id}")
async def download_batch_result(job_id: str, current_user: dict = None):
    """
    Download batch ZIP result
    Supports both local and S3 storage
    """
    status = batch_service.get_batch_status(job_id)
    if not status or status['status'] != 'COMPLETED':
        raise HTTPException(status_code=400, detail="Job not completed")
    
    # Trigger On-Demand Certificate Generation if needed
    output_file = batch_service.generate_certificates_zip(job_id)
    
    # Fallback to stored path if generation returns nothing (e.g. invalid job)
    if not output_file:
        status = batch_service.get_batch_status(job_id)
        output_file = status.get('output_file')
        
    if not output_file:
        raise HTTPException(status_code=404, detail="Output file not found")
    
    # Check if S3 URL
    if output_file.startswith('s3://'):
        # Generate presigned URL for S3
        key = output_file.replace('s3://', '').split('/', 1)[1]
        download_url = storage.generate_download_url(key)
        return {"download_url": download_url, "expires_in": 3600}
    else:
        # Local file
        if not os.path.exists(output_file):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(output_file, media_type='application/zip', filename=os.path.basename(output_file))

@router.get("/template")
async def download_csv_template():
    """Download sample CSV template."""
    return {"template": generate_sample_csv()}
