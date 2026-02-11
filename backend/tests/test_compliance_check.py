"""
Tests for compliance check endpoint
"""
import pytest
from fastapi import status

class TestComplianceCheck:
    """Test compliance check functionality"""
    
    def test_check_valid_gstin(self, client, test_db, sample_gstin):
        """Test compliance check with valid GSTIN"""
        response = client.post("/api/v1/compliance/check", json={
            "gstin": sample_gstin,
            "amount": 50000
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "decision" in data
        assert data["decision"] in ["PROCEED", "STOP", "HOLD"]
        assert "gstin" in data
        assert data["gstin"] == sample_gstin
        assert "vendor_name" in data
        assert "risk_level" in data
    
    def test_check_invalid_gstin_format(self, client, test_db):
        """Test compliance check with invalid GSTIN format"""
        response = client.post("/api/v1/compliance/check", json={
            "gstin": "INVALID",
            "amount": 50000
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid GSTIN format" in response.json()["detail"]
    
    def test_check_invalid_amount(self, client, test_db, sample_gstin):
        """Test compliance check with invalid amount"""
        response = client.post("/api/v1/compliance/check", json={
            "gstin": sample_gstin,
            "amount": -1000
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Amount must be positive" in response.json()["detail"]
    
    def test_check_zero_amount(self, client, test_db, sample_gstin):
        """Test compliance check with zero amount"""
        response = client.post("/api/v1/compliance/check", json={
            "gstin": sample_gstin,
            "amount": 0
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_check_missing_gstin(self, client, test_db):
        """Test compliance check with missing GSTIN"""
        response = client.post("/api/v1/compliance/check", json={
            "amount": 50000
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_check_missing_amount(self, client, test_db, sample_gstin):
        """Test compliance check with missing amount"""
        response = client.post("/api/v1/compliance/check", json={
            "gstin": sample_gstin
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_check_response_structure(self, client, test_db, sample_gstin):
        """Test that response has all required fields"""
        response = client.post("/api/v1/compliance/check", json={
            "gstin": sample_gstin,
            "amount": 50000
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Required fields
        required_fields = ["decision", "gstin", "vendor_name", "risk_level", "reason"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_check_performance(self, client, test_db, sample_gstin):
        """Test that compliance check is fast (< 200ms)"""
        import time
        
        start = time.time()
        response = client.post("/api/v1/compliance/check", json={
            "gstin": sample_gstin,
            "amount": 50000
        })
        duration = (time.time() - start) * 1000  # Convert to ms
        
        assert response.status_code == status.HTTP_200_OK
        assert duration < 200, f"Check took {duration}ms, expected < 200ms"
