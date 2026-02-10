"""
TaxPay Guard - Tally Integration API Routes
Fast endpoint optimized for Tally TDL HTTP requests
Following system_workflow.md architecture
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

# Import core modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gsp_client import MockGSPProvider
from decision_engine import check_vendor
from database import save_compliance_check

router = APIRouter(prefix="/tally", tags=["Tally Integration"])

# API Key for Tally clients - must be set in environment
TALLY_API_KEY = os.getenv("TALLY_API_KEY", "tpg-demo-key-123")  # Demo key for testing


def verify_tally_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify Tally API key from request header.
    In production, each customer gets a unique API key.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401, 
            detail="Missing API key. Add X-API-Key header."
        )
    
    # TODO: In production, look up API key in database
    if x_api_key != TALLY_API_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Invalid API key"
        )
    
    return x_api_key


class TallyCheckRequest(BaseModel):
    """Request from Tally TDL plugin"""
    gstin: str
    amount: float = 0
    party_name: Optional[str] = ""
    voucher_type: Optional[str] = "Payment"


class TallyCheckResponse(BaseModel):
    """
    Response optimized for TDL parsing
    Following decision_logic.md rules:
    - STOP: Block payment (S1-S3)
    - HOLD: Warning, allow with review (H1-H3)
    - RELEASE: Allow payment (R1)
    """
    decision: str  # STOP, HOLD, RELEASE
    message: str
    can_proceed: bool  # True = allow save, False = block save
    rule_id: str
    risk_level: str
    vendor_name: Optional[str] = None
    gst_status: Optional[str] = None
    data_timestamp: str
    disclaimer: str = "Based on publicly available GST data. Not a guarantee of compliance."


@router.post("/check", response_model=TallyCheckResponse)
async def tally_compliance_check(
    request: TallyCheckRequest,
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    Fast compliance check endpoint for Tally integration.
    
    Requires: X-API-Key header
    
    Flow (from system_workflow.md):
    1. Tally TDL intercepts payment voucher save
    2. HTTPS POST with GSTIN + Amount + X-API-Key header
    3. Apply STOP rules (S1-S3) -> Block if matched
    4. Apply HOLD rules (H1-H3) -> Warn if matched
    5. RELEASE (R1) -> Allow payment
    6. Return JSON for TDL to parse
    """
    # Verify API key
    verify_tally_api_key(api_key)
    
    gstin = request.gstin.strip().upper()
    
    # Validate GSTIN format
    if len(gstin) != 15:
        return TallyCheckResponse(
            decision="STOP",
            message="Invalid GSTIN format. Payment blocked.",
            can_proceed=False,
            rule_id="E1",
            risk_level="HIGH",
            data_timestamp=datetime.now().isoformat(),
        )
    
    try:
        # 1. Fetch vendor data (from GSP or cache)
        vendor_data = MockGSPProvider.get_vendor_data(gstin)
        
        # 2. Apply decision rules (S1-S3, H1-H3, R1)
        result = check_vendor(vendor_data, request.amount)
        
        decision = result.get("decision", "HOLD")
        rule_id = result.get("rule_id", "H1")
        reason = result.get("reason", "Unable to verify compliance")
        risk_level = result.get("risk_level", "MEDIUM")
        
        # 3. Determine if payment can proceed
        # - STOP: Block (can_proceed = False)
        # - HOLD: Warn but allow (can_proceed = True with warning)
        # - RELEASE: Allow (can_proceed = True)
        if decision == "STOP":
            can_proceed = False
            message = f"🚫 PAYMENT BLOCKED: {reason}"
        elif decision == "HOLD":
            can_proceed = True  # Allow with warning
            message = f"⚠️ WARNING: {reason}. CFO review recommended."
        else:  # RELEASE
            can_proceed = True
            message = f"✅ COMPLIANT: {reason}"
        
        # 4. Log the check for audit trail
        save_compliance_check(
            gstin=gstin,
            vendor_name=vendor_data.get("legal_name", request.party_name),
            amount=request.amount,
            decision=decision,
            rule_id=rule_id,
            reason=reason,
            risk_level=risk_level,
            data_source="tally_integration",
            certificate_url=None
        )
        
        return TallyCheckResponse(
            decision=decision,
            message=message,
            can_proceed=can_proceed,
            rule_id=rule_id,
            risk_level=risk_level,
            vendor_name=vendor_data.get("legal_name"),
            gst_status=vendor_data.get("gst_status"),
            data_timestamp=datetime.now().isoformat(),
        )
        
    except Exception as e:
        # On error, default to HOLD (safe fallback)
        return TallyCheckResponse(
            decision="HOLD",
            message=f"⚠️ Unable to verify: {str(e)}. Manual check recommended.",
            can_proceed=True,
            rule_id="E2",
            risk_level="MEDIUM",
            data_timestamp=datetime.now().isoformat(),
        )


@router.get("/ping")
async def ping():
    """
    Health check endpoint for Tally TDL to verify connectivity.
    TDL can call this on Tally startup to confirm API is reachable.
    No authentication required for ping.
    """
    return {
        "status": "ok",
        "service": "TaxPay Guard",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
