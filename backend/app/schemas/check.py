from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class CheckRequest(BaseModel):
    gstin: str = Field(..., example="33AABCU9603R1ZX")
    amount: Optional[float] = 0
    party_name: Optional[str] = ""
    voucher_date: Optional[str] = ""

class CheckResponse(BaseModel):
    action: str  # BLOCK, WARN, ALLOW (for Tally compatibility)
    decision: str  # STOP, HOLD, RELEASE
    title: str
    message: str
    rule_id: str
    risk_level: str
    gstin: str
    vendor_name: str
    timestamp: str
    check_id: int
    data_source: str

class VendorDetail(BaseModel):
    gstin: str
    legal_name: str
    trade_name: str
    gst_status: str
    registration_date: str
    filing_history: List[Dict]
    decision: Dict
