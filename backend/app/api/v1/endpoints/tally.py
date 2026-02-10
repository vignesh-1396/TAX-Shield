from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
from app.services.gsp import MockGSPProvider
from app.services.decision import DecisionEngine
from app.db.crud import check as check_crud

router = APIRouter()
engine = DecisionEngine()

# API Key for Tally clients - must be set in environment
TALLY_API_KEY = os.getenv("TALLY_API_KEY", "tpg-demo-key-123")

def verify_tally_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    if x_api_key != TALLY_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

class TallyCheckRequest(BaseModel):
    gstin: str
    amount: float = 0
    party_name: Optional[str] = ""
    voucher_type: Optional[str] = "Payment"

class TallyCheckResponse(BaseModel):
    decision: str  # STOP, HOLD, RELEASE
    message: str
    can_proceed: bool
    rule_id: str
    risk_level: str
    vendor_name: Optional[str] = None
    gst_status: Optional[str] = None
    data_timestamp: str
    disclaimer: str = "Based on publicly available GST data. Not a guarantee of compliance."

@router.post("/check", response_model=TallyCheckResponse)
async def tally_compliance_check(
    request: TallyCheckRequest,
    api_key: str = Depends(verify_tally_api_key)
):
    """Compliance check optimized for Tally TDL."""
    gstin = request.gstin.strip().upper()
    
    if len(gstin) != 15:
        return TallyCheckResponse(
            decision="STOP",
            message="Invalid GSTIN format",
            can_proceed=False,
            rule_id="E1",
            risk_level="HIGH",
            data_timestamp=datetime.now().isoformat(),
        )
    
    try:
        vendor_data = MockGSPProvider.get_vendor_data(gstin)
        result = engine.check_vendor(vendor_data, request.amount)
        
        decision = result.get("decision", "HOLD")
        rule_id = result.get("rule_id", "H1")
        reason = result.get("reason", "Unable to verify compliance")
        risk_level = result.get("risk_level", "MEDIUM")
        
        if decision == "STOP":
            can_proceed = False
            message = f"🚫 PAYMENT BLOCKED: {reason}"
        elif decision == "HOLD":
            can_proceed = True
            message = f"⚠️ WARNING: {reason}"
        else:
            can_proceed = True
            message = f"✅ COMPLIANT: {reason}"
        
        check_crud.save_compliance_check(
            gstin=gstin,
            vendor_name=vendor_data.get("legal_name", request.party_name),
            amount=request.amount,
            decision=decision,
            rule_id=rule_id,
            reason=reason,
            risk_level=risk_level,
            data_source="tally_integration"
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
        return TallyCheckResponse(
            decision="HOLD",
            message=f"⚠️ Error: {str(e)}",
            can_proceed=True,
            rule_id="E2",
            risk_level="MEDIUM",
            data_timestamp=datetime.now().isoformat(),
        )

@router.get("/ping")
async def ping():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
