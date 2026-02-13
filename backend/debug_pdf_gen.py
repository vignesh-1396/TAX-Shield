import os
import sys
import logging
import logging
# from app.db.session import SessionLocal # Not needed
from app.services import batch as batch_service
from app.db.crud import batch as batch_crud

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_generation(job_id):
    print(f"Debugging job: {job_id}")
    
    # Check items
    # items = batch_crud.get_batch_items(job_id, status="SUCCESS")
    items = batch_crud.get_batch_items(job_id) # Get all items
    print(f"Found {len(items)} total items")
    
    success_count = sum(1 for i in items if i['status'] == 'SUCCESS')
    failed_count = sum(1 for i in items if i['status'] == 'FAILED')
    pending_count = sum(1 for i in items if i['status'] == 'PENDING')
    
    print(f"Status breakdown: Success={success_count}, Failed={failed_count}, Pending={pending_count}")
    
    if items:
        print(f"Sample item status: {items[0]['status']}")
        print(f"Sample item error: {items[0].get('error_message')}")

    if success_count == 0:
        print("No successful items to generate PDFs for!")
        return

    # Check vendor data caching
    from app.db.crud.vendor import get_cached_vendor
    first_item = items[0]
    gstin = first_item['gstin']
    print(f"Checking cache for GSTIN: {gstin}")
    
    vendor_data = get_cached_vendor(gstin)
    if vendor_data:
        print("✅ Vendor data found in cache")
    else:
        print("❌ Vendor data NOT found in cache")
        
    print("Running generate_certificates_zip...")
    try:
        result_path = batch_service.generate_certificates_zip(job_id)
        print(f"Result path: {result_path}")
        
        # Check certificates dir
        batch_dir = os.path.join(batch_service.BATCH_OUTPUT_DIR, job_id)
        certs_dir = os.path.join(batch_dir, "certificates")
        if os.path.exists(certs_dir):
            files = os.listdir(certs_dir)
            print(f"Certificates generated: {len(files)}")
            if len(files) > 0:
                print(f"Sample: {files[0]}")
        else:
            print("Certificates dir does not exist!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    job_id = "366c8fd1-4e05-4f80-a95c-6d8f4f8efbe8"
    debug_generation(job_id)
