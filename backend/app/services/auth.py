from datetime import timedelta
from typing import Optional, Dict
from app.core import security
from app.core.config import settings
from app.db.crud import user as user_crud

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    user = user_crud.get_user_by_email(email)
    if not user:
        return None
    if not security.verify_password(password, user["password_hash"]):
        return None
    
    # Update last login
    user_crud.update_last_login(user["id"])
    
    # Return user without password
    user_data = user.copy()
    del user_data["password_hash"]
    return user_data

def create_new_user(email: str, password: str, name: str, company_name: str = None) -> Dict:
    # Check if exists
    if user_crud.get_user_by_email(email):
        raise ValueError("Email already registered")
    
    password_hash = security.get_password_hash(password)
    return user_crud.create_user(
        email=email,
        password_hash=password_hash,
        name=name,
        company_name=company_name
    )

def generate_token_response(user: Dict) -> Dict:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user["id"], expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user
    }
