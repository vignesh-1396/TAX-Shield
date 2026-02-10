from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import os
from app.services import batch as batch_service
from app.utils.csv_parser import parse_csv_content, generate_sample_csv
from app.api.deps import get_current_user

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VENDORS_PER_BATCH = 500

@router.post("/upload")
async def upload_batch(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a CSV for batch processing."""
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
    
    result = batch_service.create_batch(items, file.filename, user_id=current_user.get("id"))
    
    if len(items) <= 100:
        process_result = batch_service.process_batch_sync(result['job_id'])
        return {**result, **process_result, "parse_errors": errors[:5]}
    
    return {**result, "message": "Batch created and queued", "parse_errors": errors[:5]}

@router.get("/status/{job_id}")
async def get_job_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """Get batch job status."""
    status = batch_service.get_batch_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@router.get("/download/{job_id}")
async def download_batch_result(job_id: str, current_user: dict = Depends(get_current_user)):
    """Download batch ZIP result."""
    status = batch_service.get_batch_status(job_id)
    if not status or status['status'] != 'COMPLETED':
        raise HTTPException(status_code=400, detail="Job not completed")
    
    output_file = status.get('output_file')
    if not output_file or not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(output_file, media_type='application/zip', filename=os.path.basename(output_file))

@router.get("/template")
async def download_csv_template():
    """Download sample CSV template."""
    return {"template": generate_sample_csv()}
