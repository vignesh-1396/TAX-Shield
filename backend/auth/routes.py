"""
TaxPay Guard - Auth API Routes
Endpoints for user registration, login, and token management
"""
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional
import re

from .models import UserRegister, UserLogin, TokenResponse, UserResponse
from .service import create_user, login_user, get_user_by_id
from .jwt_handler import get_user_id_from_token

# Rate limiting - import limiter from server
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def validate_password_complexity(password: str) -> tuple[bool, str]:
    """
    Validate password meets complexity requirements.
    Returns (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, ""


def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to get current authenticated user.
    Use in endpoints that require authentication.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")  # Rate limit: 5 registrations per minute
async def register(request: Request, data: UserRegister):
    """
    Register a new user account.
    
    Password Requirements:
    - Minimum 6 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    
    Returns JWT token on successful registration.
    """
    # Validate password complexity
    is_valid, error_msg = validate_password_complexity(data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        # Create user
        user = create_user(
            email=data.email,
            password=data.password,
            name=data.name,
            company_name=data.company_name
        )
        
        # Auto-login after registration
        result = login_user(data.email, data.password)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")  # Rate limit: 10 login attempts per minute
async def login(request: Request, data: UserLogin):
    """
    Login with email and password.
    
    Rate limited to prevent brute force attacks.
    
    Returns JWT token on successful login.
    """
    result = login_user(data.email, data.password)
    
    if not result:
        # Generic error to prevent username enumeration
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return result


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    Requires: Authorization header with Bearer token
    """
    return current_user


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user.
    
    Note: With JWT tokens, logout is handled client-side by deleting the token.
    This endpoint is provided for API completeness.
    """
    return {"message": "Successfully logged out", "user_id": current_user["id"]}
