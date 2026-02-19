from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class CheckRequest(BaseModel):
    gstin: str = Field(..., example="33AABCU9603R1ZX")
    amount: Optional[float] = 0
    party_name: Optional[str] = ""
    voucher_date: Optional[str] = ""

class CheckResponse(BaseModel):
    """Optimized response with minimal payload for faster API responses"""
    action: str  # BLOCK, WARN, ALLOW (for Tally compatibility)
    decision: str  # STOP, HOLD, RELEASE
    title: str
    message: str
    rule_id: str
    risk_level: str
    gstin: str
    vendor_name: str
    check_id: int
    certificate_url: str
    data_source: Optional[str] = "GSP_LIVE"
    timestamp: Optional[str] = None

class CheckResponseDetailed(BaseModel):
    """Detailed response with all fields (for backward compatibility)"""
    action: str
    decision: str
    title: str
    message: str
    rule_id: str
    risk_level: str
    gstin: str
    vendor_name: str
    timestamp: str
    check_id: int
    data_source: str
    certificate_url: str

class VendorDetail(BaseModel):
    gstin: str
    legal_name: str
    trade_name: str
    gst_status: str
    registration_date: str
    filing_history: List[Dict]
    decision: Dict
