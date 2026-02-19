from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from token."""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


# ============================================
# Security Headers Middleware
# ============================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to protect against common vulnerabilities
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Strict Transport Security (HSTS)
        # Forces HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy (CSP)
        # Relaxed for local development communication
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:3000 http://localhost:8000"
        )
        
        # X-Frame-Options
        # Prevents clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options
        # Prevents MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection
        # Enables browser XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        # Controls referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature Policy)
        # Restricts browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        return response


def setup_security_headers(app):
    """Add security headers middleware to app"""
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("Security headers middleware configured")
