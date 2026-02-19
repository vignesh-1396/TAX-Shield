"""
ITC Shield - Main API Server
FastAPI backend for GST compliance checking
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import our modules
from gsp_client import MockGSPProvider
from decision_engine import DecisionEngine
import database as db
from pdf_generator import generate_certificate
from batch.routes import router as batch_router
from auth.routes import router as auth_router
from tally.routes import router as tally_router

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="TaxPay Guard API",
    description="GST Vendor Compliance Check API for TaxPay Protection",
    version="1.0.0"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for web frontend and Tally
# TODO: Restrict origins in production
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add production domains here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize decision engine
engine = DecisionEngine()

# Include routers
app.include_router(auth_router)
app.include_router(batch_router)
app.include_router(tally_router)

# Request/Response Models
class CheckRequest(BaseModel):
    gstin: str
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
    filing_history: list
    decision: dict

# API Endpoints

@app.get("/")
def home():
    """Health check endpoint"""
    return {
        "status": "TaxPay Guard API is Running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/check_compliance", response_model=CheckResponse)
async def check_compliance(request: CheckRequest):
    """
    Main compliance check endpoint.
    Called by Tally TDL or Web Dashboard.
    """
    gstin = request.gstin.strip().upper()
    
    # Validate GSTIN format
    if len(gstin) != 15:
        raise HTTPException(status_code=400, detail="Invalid GSTIN format. Must be 15 characters.")
    
    print(f"[{datetime.now()}] Checking: {request.party_name} ({gstin})")
    
    # Fetch vendor data from GSP (or cache)
    vendor_data = db.get_cached_vendor(gstin, max_age_hours=24)
    data_source = "CACHE"
    
    if not vendor_data:
        vendor_data = MockGSPProvider.get_vendor_data(gstin)
        data_source = "GSP_LIVE"
        if vendor_data:
            db.save_vendor(vendor_data)
    
    # Run decision engine
    result = engine.check_vendor(vendor_data, request.amount)
    
    # Map decision to Tally action
    action_map = {
        "STOP": "BLOCK",
        "HOLD": "WARN", 
        "RELEASE": "ALLOW"
    }
    
    title_map = {
        "STOP": "🚫 PAYMENT BLOCKED",
        "HOLD": "⚠️ CFO REVIEW REQUIRED",
        "RELEASE": "✅ PAYMENT APPROVED"
    }
    
    # Save to database
    check_id = db.save_compliance_check(
        gstin=gstin,
        vendor_name=vendor_data.get("legal_name", request.party_name) if vendor_data else request.party_name,
        amount=request.amount,
        decision=result["decision"],
        rule_id=result["rule_id"],
        reason=result["reason"],
        risk_level=result["risk_level"],
        data_source=data_source
    )
    
    return CheckResponse(
        action=action_map[result["decision"]],
        decision=result["decision"],
        title=title_map[result["decision"]],
        message=result["reason"],
        rule_id=result["rule_id"],
        risk_level=result["risk_level"],
        gstin=gstin,
        vendor_name=vendor_data.get("legal_name", "") if vendor_data else "",
        timestamp=result["timestamp_display"],
        check_id=check_id,
        data_source=data_source
    )

@app.get("/vendor/{gstin}")
async def get_vendor_details(gstin: str):
    """Get detailed vendor information with decision"""
    gstin = gstin.strip().upper()
    
    # Fetch vendor data
    vendor_data = MockGSPProvider.get_vendor_data(gstin)
    if not vendor_data:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Run decision
    result = engine.check_vendor(vendor_data)
    
    return {
        "gstin": gstin,
        "legal_name": vendor_data.get("legal_name"),
        "trade_name": vendor_data.get("trade_name"),
        "gst_status": vendor_data.get("gst_status"),
        "registration_date": vendor_data.get("registration_date"),
        "filing_history": vendor_data.get("filing_history", []),
        "decision": result
    }

@app.get("/history")
async def get_check_history(limit: int = 50):
    """Get recent compliance checks"""
    checks = db.get_recent_checks(limit)
    return {"checks": checks, "total": len(checks)}

@app.get("/history/{gstin}")
async def get_vendor_history(gstin: str):
    """Get compliance history for a specific vendor"""
    gstin = gstin.strip().upper()
    checks = db.get_checks_by_gstin(gstin)
    return {"gstin": gstin, "checks": checks, "total": len(checks)}

@app.get("/test-scenarios")
async def test_scenarios():
    """
    Test endpoint showing all mock scenarios.
    Use these GSTINs to test different rules:
    """
    scenarios = {
        "STOP - S1 (Cancelled)": "01AABCU9603R1ZX",
        "STOP - S2 (Suspended)": "02AABCU9603R1ZX", 
        "STOP - S3 (Non-Filer)": "03AABCU9603R1ZX",
        "HOLD - H1 (Late Filer)": "04AABCU9603R1ZX",
        "HOLD - H2 (New Vendor)": "05AABCU9603R1ZX",
        "HOLD - H3 (Name Mismatch)": "06AABCU9603R1ZX",
        "RELEASE - R1 (Compliant)": "33AABCU9603R1ZX"
    }
    return {
        "message": "Use these GSTINs to test each decision rule",
        "scenarios": scenarios
    }

@app.get("/certificate/{check_id}")
async def download_certificate(check_id: int):
    """
    Download Due Diligence Certificate PDF for a compliance check.
    """
    # Get check details from database
    check = db.get_check_by_id(check_id)
    if not check:
        raise HTTPException(status_code=404, detail="Check not found")
    
    # Fetch full vendor details for the certificate
    # We need this for filing history and other details not in the check record
    vendor_data = db.get_cached_vendor(check["gstin"])
    
    filing_history = vendor_data.get("filing_history", []) if vendor_data else []
    registration_date = vendor_data.get("registration_date", "") if vendor_data else ""
    gst_status = vendor_data.get("gst_status", "") if vendor_data else ""
    
    # Determine Rule 37A Status based on decision
    rule_37a_status = "Clean"
    if check["decision"] == "STOP":
        rule_37a_status = "Failed"
    elif check["decision"] == "HOLD":
        rule_37a_status = "Review Required"
    
    # Prepare data for PDF
    check_data = {
        "gstin": check["gstin"],
        "vendor_name": check["vendor_name"] or "Unknown Vendor",
        "amount": check["amount"],
        "decision": check["decision"],
        "rule_id": check["rule_id"],
        "reason": check["reason"],          # For backward compatibility
        "decision_reason": check["reason"], # For new template
        "risk_level": check["risk_level"],
        "check_id": check["id"],
        "timestamp": check["created_at"],
        "data_source": check["data_source"],
        "filing_history": filing_history,
        "registration_date": registration_date,
        "gst_status": gst_status,
        "rule_37a_status": rule_37a_status
    }
    
    # Generate PDF (or HTML fallback)
    # This now returns bytes directly
    pdf_bytes = generate_certificate(check_data)
    
    # Check if we got a valid PDF or HTML fallback
    is_pdf = pdf_bytes.startswith(b"%PDF")
    
    if is_pdf:
        media_type = "application/pdf"
        ext = "pdf"
    else:
        media_type = "text/html"
        ext = "html"
    
    # Return as downloadable file
    filename = f"TaxPayGuard_Cert_{check['gstin']}_{check_id}.{ext}"
    return Response(
        content=pdf_bytes,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  TaxPay Guard API Server")
    print("="*50)
    print(f"  Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Endpoints:")
    print("    - POST /check_compliance  (Main check)")
    print("    - GET  /vendor/{gstin}    (Vendor details)")
    print("    - GET  /history           (Audit trail)")
    print("    - GET  /test-scenarios    (Test GSTINs)")
    print("    - GET  /docs              (API Documentation)")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
