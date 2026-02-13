#!/usr/bin/env python3
import requests
import time
import zipfile
import os

API_URL = "http://localhost:8000"

print("🚀 Testing Batch Upload...")

# Step 1: Upload CSV
print("\n1️⃣ Uploading test_batch.csv...")
with open('test_batch.csv', 'rb') as f:
    response = requests.post(
        f"{API_URL}/api/v1/batch/upload",
        files={'file': ('test_batch.csv', f, 'text/csv')}
    )

if response.status_code != 200:
    print(f"❌ Upload failed: {response.text}")
    exit(1)

data = response.json()
job_id = data['job_id']
print(f"✅ Upload successful! Job ID: {job_id}")
print(f"   Status: {data.get('status')}")
print(f"   Total vendors: {data.get('total_vendors')}")

# Step 2: Check if already completed (small batches process immediately)
if data.get('status') == 'COMPLETED':
    print("\n✅ Batch already completed (processed synchronously)")
else:
    # Wait for processing
    print("\n2️⃣ Waiting for batch processing...")
    max_wait = 60
    waited = 0
    
    while waited < max_wait:
        time.sleep(2)
        waited += 2
        
        status_response = requests.get(f"{API_URL}/api/v1/batch/status/{job_id}")
        status_data = status_response.json()
        
        print(f"   Progress: {status_data.get('processed', 0)}/{status_data.get('total', 0)} "
              f"(Success: {status_data.get('success', 0)}, Failed: {status_data.get('failed', 0)})")
        
        if status_data.get('status') == 'COMPLETED':
            print("✅ Batch processing completed!")
            break
    else:
        print("⏱️ Timeout waiting for batch completion")
        exit(1)

# Step 3: Download ZIP
print("\n3️⃣ Downloading results ZIP...")
download_response = requests.get(f"{API_URL}/api/v1/batch/download/{job_id}")

if download_response.status_code != 200:
    print(f"❌ Download failed: {download_response.text}")
    exit(1)

zip_path = f"batch_result_{job_id}.zip"
with open(zip_path, 'wb') as f:
    f.write(download_response.content)

print(f"✅ Downloaded: {zip_path}")
print(f"   Size: {len(download_response.content)} bytes")

# Step 4: Extract and show contents
print("\n4️⃣ ZIP Contents:")
print("=" * 60)

with zipfile.ZipFile(zip_path, 'r') as zipf:
    file_list = zipf.namelist()
    
    for file in sorted(file_list):
        file_info = zipf.getinfo(file)
        size = file_info.file_size
        
        if file.endswith('/'):
            print(f"📁 {file}")
        else:
            print(f"📄 {file} ({size} bytes)")
    
    print("=" * 60)
    print(f"\n📊 Total files: {len(file_list)}")
    
    # Show results.csv content
    if 'results.csv' in file_list:
        print("\n5️⃣ Preview of results.csv:")
        print("=" * 60)
        csv_content = zipf.read('results.csv').decode('utf-8')
        lines = csv_content.split('\n')[:6]  # Show first 6 lines
        for line in lines:
            print(line)
        if len(csv_content.split('\n')) > 6:
            print("...")
        print("=" * 60)
    
    # Show summary.txt content
    if 'summary.txt' in file_list:
        print("\n6️⃣ Summary:")
        print("=" * 60)
        summary_content = zipf.read('summary.txt').decode('utf-8')
        print(summary_content)
        print("=" * 60)

print("\n✅ Test completed successfully!")
print(f"\n📦 ZIP file saved as: {zip_path}")
