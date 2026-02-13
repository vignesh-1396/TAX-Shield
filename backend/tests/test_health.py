"""
Tests for health check endpoints
"""
import pytest
from fastapi import status

class TestHealthCheck:
    """Test health check endpoints"""
    
    def test_health_endpoint(self, client):
        """Test basic health check"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_ready_endpoint(self, client):
        """Test readiness check"""
        response = client.get("/api/v1/health/ready")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "database" in data
        assert "redis" in data
    
    def test_live_endpoint(self, client):
        """Test liveness check"""
        response = client.get("/api/v1/health/live")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == "alive"
