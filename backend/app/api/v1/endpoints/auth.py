from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.token import Token, UserRegister, UserLogin, UserResponse
from app.services import auth as auth_service
from app.api.deps import limiter
import re

router = APIRouter()

def validate_password_complexity(password: str) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, ""

@router.post("/register", response_model=Token)
@limiter.limit("5/minute")
async def register(request: Request, data: UserRegister):
    is_valid, error_msg = validate_password_complexity(data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        user = auth_service.create_new_user(
            email=data.email,
            password=data.password,
            name=data.name,
            company_name=data.company_name
        )
        return auth_service.generate_token_response(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, data: UserLogin):
    user = auth_service.authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return auth_service.generate_token_response(user)
