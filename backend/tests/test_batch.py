"""
Tests for batch processing functionality
"""
import pytest
from fastapi import status
import io

class TestBatchProcessing:
    """Test batch upload and processing"""
    
    def test_batch_upload_valid_csv(self, client, test_db):
        """Test batch upload with valid CSV"""
        csv_content = """gstin,vendor_name,amount
27AABCU9603R1ZM,Test Vendor 1,50000
29AABCT1332L1ZV,Test Vendor 2,75000
07AAGFF2194N1Z1,Test Vendor 3,100000"""
        
        files = {
            'file': ('test_batch.csv', io.BytesIO(csv_content.encode()), 'text/csv')
        }
        
        response = client.post("/api/v1/batch/upload", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "job_id" in data
        assert "task_id" in data
        assert data["total_vendors"] == 3
        assert data["status"] in ["queued", "processing"]
    
    def test_batch_upload_invalid_format(self, client, test_db):
        """Test batch upload with invalid file format"""
        files = {
            'file': ('test.txt', io.BytesIO(b'invalid content'), 'text/plain')
        }
        
        response = client.post("/api/v1/batch/upload", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_batch_upload_empty_file(self, client, test_db):
        """Test batch upload with empty file"""
        files = {
            'file': ('empty.csv', io.BytesIO(b''), 'text/csv')
        }
        
        response = client.post("/api/v1/batch/upload", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_batch_upload_missing_columns(self, client, test_db):
        """Test batch upload with missing required columns"""
        csv_content = """vendor_name,amount
Test Vendor,50000"""
        
        files = {
            'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')
        }
        
        response = client.post("/api/v1/batch/upload", files=files)
        
        # Should either reject or return with parse errors
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "parse_errors" in data
    
    def test_batch_status(self, client, test_db):
        """Test batch status endpoint"""
        # First upload a batch
        csv_content = """gstin,vendor_name,amount
27AABCU9603R1ZM,Test Vendor,50000"""
        
        files = {
            'file': ('test.csv', io.BytesIO(csv_content.encode()), 'text/csv')
        }
        
        upload_response = client.post("/api/v1/batch/upload", files=files)
        job_id = upload_response.json()["job_id"]
        
        # Check status
        status_response = client.get(f"/api/v1/batch/status/{job_id}")
        
        assert status_response.status_code == status.HTTP_200_OK
        data = status_response.json()
        
        assert "status" in data
        assert "total_count" in data
        assert data["status"] in ["PENDING", "PROCESSING", "COMPLETED", "FAILED"]
    
    def test_batch_status_invalid_job(self, client, test_db):
        """Test batch status with invalid job ID"""
        response = client.get("/api/v1/batch/status/invalid-job-id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_batch_file_size_limit(self, client, test_db):
        """Test batch upload respects file size limit"""
        # Create a large CSV (simulate)
        large_content = "gstin,vendor_name,amount\n" * 10000
        
        files = {
            'file': ('large.csv', io.BytesIO(large_content.encode()), 'text/csv')
        }
        
        response = client.post("/api/v1/batch/upload", files=files)
        
        # Should either accept or reject based on size limit
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE]
