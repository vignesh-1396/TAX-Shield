"""
API Key Authentication Dependency
"""
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.db.crud.api_keys import validate_api_key, log_api_key_usage
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_api_key_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Validate API key from Authorization header
    
    Usage in endpoints:
        @router.get("/protected")
        async def protected_route(user: dict = Depends(get_api_key_user)):
            # user contains: user_id, email, name, permissions
            return {"message": f"Hello {user['name']}"}
    """
    api_key = credentials.credentials
    
    # Validate key
    user_info = validate_api_key(api_key)
    
    if not user_info:
        logger.warning(f"Invalid API key attempt from {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log usage (async in background would be better)
    try:
        log_api_key_usage(
            key_id=user_info["key_id"],
            endpoint=str(request.url.path),
            method=request.method,
            status_code=200,  # Will be updated by middleware
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "")
        )
    except Exception as e:
        logger.error(f"Failed to log API key usage: {e}")
    
    return user_info


async def get_optional_api_key_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[Dict[str, Any]]:
    """
    Optional API key authentication
    Returns None if no key provided, validates if present
    """
    if not credentials:
        return None
    
    return validate_api_key(credentials.credentials)


def require_permission(permission: str):
    """
    Decorator to require specific permission
    
    Usage:
        @router.post("/admin-only")
        async def admin_route(user: dict = Depends(require_permission("admin"))):
            return {"message": "Admin access granted"}
    """
    async def permission_checker(
        user: Dict[str, Any] = Security(get_api_key_user)
    ) -> Dict[str, Any]:
        if permission not in user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return user
    
    return permission_checker
