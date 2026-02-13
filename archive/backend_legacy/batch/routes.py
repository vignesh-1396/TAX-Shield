"""
TaxPay Guard - Batch API Routes
API endpoints for batch vendor compliance checking
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import os

from .csv_parser import parse_csv_content, generate_sample_csv
from .service import create_batch, process_batch_sync, get_batch_status

# Import auth dependency
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.routes import get_current_user

router = APIRouter(prefix="/batch", tags=["Batch Processing"])

# Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB max file size
MAX_VENDORS_PER_BATCH = 500  # Maximum vendors in one batch


@router.post("/upload")
async def upload_batch(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)  # Require authentication
):
    """
    Upload a CSV file with vendor GSTINs for batch processing.
    
    Requires: Authentication (Bearer token)
    
    Expected CSV format:
    GSTIN,Vendor Name,Amount
    33AABCU9603R1ZX,Vendor A,50000
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Check file size before reading
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to start
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Read and parse CSV
    content = await file.read()
    items, errors = parse_csv_content(content)
    
    if not items:
        raise HTTPException(
            status_code=400, 
            detail={
                "message": "No valid vendors found in CSV",
                "errors": errors[:10]  # Return first 10 errors
            }
        )
    
    # Check vendor count limit
    if len(items) > MAX_VENDORS_PER_BATCH:
        raise HTTPException(
            status_code=400,
            detail=f"Too many vendors. Maximum is {MAX_VENDORS_PER_BATCH} per batch"
        )
    
    # Create batch job with user ID
    result = create_batch(items, file.filename, user_id=current_user.get("id"))
    
    # For MVP: Process synchronously (will be async with Celery later)
    # This blocks until complete - OK for small batches
    if len(items) <= 100:
        process_result = process_batch_sync(result['job_id'])
        return {
            **result,
            **process_result,
            "parse_errors": errors[:5] if errors else []
        }
    
    # For larger batches, return immediately and process async
    # TODO: Add Celery task here
    return {
        **result,
        "message": f"Batch job created with {len(items)} vendors. Check status endpoint for progress.",
        "parse_errors": errors[:5] if errors else []
    }


@router.get("/status/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the status of a batch job (authenticated)"""
    status = get_batch_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # TODO: Check if job belongs to current user (multi-tenant)
    
    return status


@router.get("/download/{job_id}")
async def download_batch_result(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download the ZIP file containing all certificates (authenticated)"""
    status = get_batch_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if status['status'] != 'COMPLETED':
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not complete. Current status: {status['status']}"
        )
    
    output_file = status.get('output_file')
    if not output_file or not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_file,
        media_type='application/zip',
        filename=os.path.basename(output_file)
    )


@router.get("/template")
async def download_csv_template():
    """Download a sample CSV template (public endpoint)"""
    return {
        "template": generate_sample_csv(),
        "instructions": "Save this as a .csv file. Required column: GSTIN. Optional: Vendor Name, Amount"
    }
