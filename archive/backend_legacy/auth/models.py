"""
TaxPay Guard - Auth Pydantic Models
Request/Response schemas for authentication endpoints
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    name: str = Field(..., min_length=2, description="Full name")
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    """Request model for login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response model for user data (no password)"""
    id: str
    email: str
    name: str
    company_name: Optional[str]
    role: str
    created_at: str


class TokenResponse(BaseModel):
    """Response model for login success"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds
    user: UserResponse


class AuthError(BaseModel):
    """Error response"""
    detail: str
