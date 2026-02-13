"""
API Key Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from app.api.deps import get_current_user
from app.db.crud import api_keys as api_key_crud
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateAPIKeyRequest(BaseModel):
    key_name: str = Field(..., min_length=1, max_length=100, description="Descriptive name for the API key")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days (optional)")
    permissions: str = Field("read,write", description="Comma-separated permissions")


class APIKeyResponse(BaseModel):
    id: str
    key_name: str
    api_key: Optional[str] = None  # Only included on creation
    prefix: str
    created_at: str
    expires_at: Optional[str]
    is_active: bool
    permissions: str
    usage_count: int = 0
    last_used_at: Optional[str] = None


@router.post("/", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new API key
    
    **IMPORTANT:** The full API key is only shown once during creation.
    Save it securely - you won't be able to see it again!
    """
    try:
        key_data = api_key_crud.create_api_key(
            user_id=current_user["id"],
            key_name=request.key_name,
            expires_in_days=request.expires_in_days,
            permissions=request.permissions
        )
        
        return APIKeyResponse(
            id=key_data["id"],
            key_name=key_data["key_name"],
            api_key=key_data["api_key"],  # Full key - only shown once!
            prefix=key_data["prefix"],
            created_at=key_data["created_at"],
            expires_at=key_data["expires_at"],
            is_active=True,
            permissions=key_data["permissions"],
            usage_count=0
        )
    
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(current_user: dict = Depends(get_current_user)):
    """
    List all API keys for the current user
    
    Note: The actual API keys are never returned, only prefixes for identification.
    """
    try:
        keys = api_key_crud.get_user_api_keys(current_user["id"])
        
        return [
            APIKeyResponse(
                id=key["id"],
                key_name=key["key_name"],
                prefix=key["prefix"],
                created_at=key["created_at"],
                last_used_at=key["last_used_at"],
                expires_at=key["expires_at"],
                is_active=key["is_active"],
                permissions=key["permissions"],
                usage_count=key["usage_count"]
            )
            for key in keys
        ]
    
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API keys"
        )


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke (deactivate) an API key
    
    The key will be deactivated but not deleted, preserving usage history.
    """
    success = api_key_crud.revoke_api_key(key_id, current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found or already revoked"
        )
    
    return {"message": "API key revoked successfully"}


@router.delete("/{key_id}/permanent")
async def delete_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Permanently delete an API key
    
    **WARNING:** This action cannot be undone. All usage history will be lost.
    """
    success = api_key_crud.delete_api_key(key_id, current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return {"message": "API key deleted permanently"}


@router.get("/{key_id}/usage")
async def get_api_key_usage(
    key_id: str,
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """
    Get usage statistics for an API key
    
    Returns call counts by endpoint and by day for the specified period.
    """
    try:
        # Verify key belongs to user
        user_keys = api_key_crud.get_user_api_keys(current_user["id"])
        if not any(k["id"] == key_id for k in user_keys):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        stats = api_key_crud.get_api_key_usage_stats(key_id, days)
        return stats
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get API key usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics"
        )
