"""
GSTR-2B API Endpoints
Handles OTP flow and GSTR-2B data synchronization
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.api.deps import get_current_user
from app.services.gsp import get_gsp_provider
from app.db.crud import gst_credentials, gstr2b_data
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class ConnectGSTRequest(BaseModel):
    gstin: str = Field(..., min_length=15, max_length=15, description="GSTIN to connect")
    username: str = Field(..., description="GST Portal username (usually GSTIN or email)")


class VerifyOTPRequest(BaseModel):
    gstin: str = Field(..., min_length=15, max_length=15)
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")
    transaction_id: str = Field(..., description="Transaction ID from connect request")


class SyncGSTR2BRequest(BaseModel):
    gstin: str = Field(..., min_length=15, max_length=15)
    return_period: str = Field(..., pattern=r"^\d{6}$", description="Return period in MMYYYY format")


class GSTConnectionResponse(BaseModel):
    gstin: str
    is_connected: bool
    token_expiry: Optional[str] = None
    last_synced: Optional[str] = None


@router.post("/connect", status_code=status.HTTP_200_OK)
async def request_gst_otp(
    request: ConnectGSTRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Step 1: Request OTP for GSTR-2B access.
    
    This initiates the OTP flow. User will receive OTP on their registered mobile.
    """
    try:
        gsp = get_gsp_provider()
        
        # Check if GSP provider supports GSTR-2B
        if not hasattr(gsp, 'request_otp'):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="GSTR-2B is only available with Sandbox GSP provider"
            )
        
        # Request OTP from GSP
        result = gsp.request_otp(request.gstin, request.username)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to request OTP. Please check GSTIN and username."
            )
        
        logger.info(f"OTP requested successfully for GSTIN: {request.gstin}")
        
        return {
            "message": "OTP sent successfully to registered mobile",
            "transaction_id": result["transaction_id"],
            "gstin": request.gstin
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request OTP"
        )


@router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_gst_otp(
    request: VerifyOTPRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Step 2: Verify OTP and establish GSTR-2B connection.
    
    This verifies the OTP and stores the auth token for future GSTR-2B fetches.
    """
    try:
        gsp = get_gsp_provider()
        
        if not hasattr(gsp, 'verify_otp'):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="GSTR-2B is only available with Sandbox GSP provider"
            )
        
        # Verify OTP with GSP
        result = gsp.verify_otp(request.gstin, request.otp, request.transaction_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP or transaction ID"
            )
        
        # Store credentials in database
        # TODO: Encrypt auth_token before storing
        credential_id = gst_credentials.create_gst_credential(
            user_id=current_user["id"],
            gstin=request.gstin,
            username=request.gstin,  # Store GSTIN as username for now
            auth_token=result["auth_token"],
            token_expiry=result["token_expiry"]
        )
        
        if not credential_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store GST credentials"
            )
        
        logger.info(f"GSTIN {request.gstin} connected successfully for user: {current_user['id']}")
        
        return {
            "message": "GSTIN connected successfully",
            "gstin": request.gstin,
            "token_expiry": result["token_expiry"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP"
        )


@router.get("/status/{gstin}", response_model=GSTConnectionResponse)
async def get_gst_connection_status(
    gstin: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Check if a GSTIN is connected and token status.
    """
    try:
        credential = gst_credentials.get_gst_credential(current_user["id"], gstin)
        
        if not credential:
            return GSTConnectionResponse(
                gstin=gstin,
                is_connected=False
            )
        
        return GSTConnectionResponse(
            gstin=gstin,
            is_connected=credential["is_active"],
            token_expiry=credential["token_expiry"],
            last_synced=credential["updated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error checking GST status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check connection status"
        )


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_gstr2b_data(
    request: SyncGSTR2BRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch and sync GSTR-2B data for a specific return period.
    
    This downloads all invoices from GSTR-2B and stores them for reconciliation.
    """
    try:
        # Get stored credentials
        credential = gst_credentials.get_gst_credential(current_user["id"], request.gstin)
        
        if not credential or not credential["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GSTIN not connected. Please connect first using /connect endpoint."
            )
        
        gsp = get_gsp_provider()
        
        if not hasattr(gsp, 'fetch_gstr2b'):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="GSTR-2B is only available with Sandbox GSP provider"
            )
        
        # Fetch GSTR-2B data from GSP
        result = gsp.fetch_gstr2b(
            gstin=request.gstin,
            return_period=request.return_period,
            auth_token=credential["auth_token"]
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch GSTR-2B data. Token may have expired."
            )
        
        # Delete existing data for this period (if re-syncing)
        gstr2b_data.delete_gstr2b_data(current_user["id"], request.return_period)
        
        # Store invoices in database
        inserted_count = gstr2b_data.bulk_insert_gstr2b_invoices(
            user_id=current_user["id"],
            invoices=result["invoices"]
        )
        
        logger.info(f"Synced {inserted_count} invoices for GSTIN: {request.gstin}, Period: {request.return_period}")
        
        return {
            "message": "GSTR-2B data synced successfully",
            "gstin": request.gstin,
            "return_period": request.return_period,
            "total_invoices": inserted_count,
            "fetched_at": result["fetched_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing GSTR-2B data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync GSTR-2B data"
        )


@router.get("/summary/{return_period}")
async def get_gstr2b_summary(
    return_period: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get summary statistics for GSTR-2B data.
    """
    try:
        summary = gstr2b_data.get_gstr2b_summary(current_user["id"], return_period)
        
        return {
            "return_period": return_period,
            **summary
        }
        
    except Exception as e:
        logger.error(f"Error fetching GSTR-2B summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch summary"
        )


@router.delete("/disconnect/{gstin}")
async def disconnect_gstin(
    gstin: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Disconnect a GSTIN (deactivate credentials).
    """
    try:
        success = gst_credentials.deactivate_gst_credential(current_user["id"], gstin)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GSTIN not found or already disconnected"
            )
        
        return {
            "message": "GSTIN disconnected successfully",
            "gstin": gstin
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting GSTIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect GSTIN"
        )
