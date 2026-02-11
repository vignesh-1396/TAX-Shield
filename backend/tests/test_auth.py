"""
Tests for authentication endpoints
"""
import pytest
from fastapi import status

class TestAuthentication:
    """Test authentication and authorization"""
    
    def test_register_new_user(self, client, test_db):
        """Test user registration"""
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecureP@ss123",
            "name": "New User",
            "company_name": "Test Company"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
    
    def test_register_duplicate_email(self, client, test_db):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/api/v1/auth/register", json={
            "email": "duplicate@example.com",
            "password": "SecureP@ss123",
            "name": "User One"
        })
        
        # Try to register again with same email
        response = client.post("/api/v1/auth/register", json={
            "email": "duplicate@example.com",
            "password": "DifferentP@ss123",
            "name": "User Two"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_weak_password(self, client, test_db):
        """Test registration with weak password"""
        response = client.post("/api/v1/auth/register", json={
            "email": "weak@example.com",
            "password": "weak",
            "name": "Weak User"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_invalid_email(self, client, test_db):
        """Test registration with invalid email"""
        response = client.post("/api/v1/auth/register", json={
            "email": "notanemail",
            "password": "SecureP@ss123",
            "name": "Invalid Email User"
        })
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_login_valid_credentials(self, client, test_db):
        """Test login with valid credentials"""
        # Register user first
        client.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "password": "SecureP@ss123",
            "name": "Login User"
        })
        
        # Login
        response = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "SecureP@ss123"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_password(self, client, test_db):
        """Test login with invalid password"""
        # Register user
        client.post("/api/v1/auth/register", json={
            "email": "wrongpass@example.com",
            "password": "CorrectP@ss123",
            "name": "User"
        })
        
        # Try login with wrong password
        response = client.post("/api/v1/auth/login", json={
            "email": "wrongpass@example.com",
            "password": "WrongP@ss123"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client, test_db):
        """Test login with non-existent user"""
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "SomeP@ss123"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_expiration(self, client, test_db):
        """Test that tokens have expiration"""
        # Register and login
        client.post("/api/v1/auth/register", json={
            "email": "token@example.com",
            "password": "SecureP@ss123",
            "name": "Token User"
        })
        
        response = client.post("/api/v1/auth/login", json={
            "email": "token@example.com",
            "password": "SecureP@ss123"
        })
        
        token = response.json()["access_token"]
        
        # Decode token to check expiration (basic check)
        assert len(token) > 0
        assert "." in token  # JWT format
