from fastapi import APIRouter, HTTPException, Depends, Response, Request
from typing import List, Optional
from datetime import datetime

from app.schemas.check import CheckRequest, CheckResponse, VendorDetail
from app.services.decision import DecisionEngine
from app.services.gsp import get_gsp_provider
from app.services.pdf import generate_certificate
from app.db.crud import vendor as vendor_crud
from app.db.crud import check as check_crud
from app.api.deps import limiter

router = APIRouter()
engine = DecisionEngine()

@router.post("/check", response_model=CheckResponse)
@limiter.limit("20/minute")
async def check_compliance(request: Request, check_request: CheckRequest):
    """Main compliance check endpoint."""
    gstin = check_request.gstin.strip().upper()
    
    if len(gstin) != 15:
        raise HTTPException(status_code=400, detail="Invalid GSTIN format. Must be 15 characters.")
    
    # Fetch vendor data from GSP (or cache)
    vendor_data = vendor_crud.get_cached_vendor(gstin, max_age_hours=24)
    data_source = "CACHE"
    
    if not vendor_data:
        provider = get_gsp_provider()
        vendor_data = provider.get_vendor_data(gstin)
        data_source = "GSP_LIVE"
        if vendor_data:
            vendor_crud.save_vendor(vendor_data)
    
    # Run decision engine
    # decision_engine.py logic expects vendor_data and amount
    result = engine.check_vendor(vendor_data, check_request.amount)
    
    # Map decision to Tally action
    action_map = {"STOP": "BLOCK", "HOLD": "WARN", "RELEASE": "ALLOW"}
    title_map = {
        "STOP": "🚫 PAYMENT BLOCKED",
        "HOLD": "⚠️ CFO REVIEW REQUIRED",
        "RELEASE": "✅ PAYMENT APPROVED"
    }
    
    # Save to database
    check_id = check_crud.save_compliance_check(
        gstin=gstin,
        vendor_name=vendor_data.get("legal_name", check_request.party_name) if vendor_data else check_request.party_name,
        amount=check_request.amount,
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

@router.get("/vendor/{gstin}", response_model=VendorDetail)
async def get_vendor_details(gstin: str):
    """Get detailed vendor information with decision."""
    gstin = gstin.strip().upper()
    provider = get_gsp_provider()
    vendor_data = provider.get_vendor_data(gstin)
    if not vendor_data:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    result = engine.check_vendor(vendor_data)
    
    return VendorDetail(
        gstin=gstin,
        legal_name=vendor_data.get("legal_name"),
        trade_name=vendor_data.get("trade_name"),
        gst_status=vendor_data.get("gst_status"),
        registration_date=vendor_data.get("registration_date"),
        filing_history=vendor_data.get("filing_history", []),
        decision=result
    )

@router.get("/history", response_model=List[dict])
async def get_check_history(limit: int = 50):
    """Get recent compliance checks."""
    return check_crud.get_recent_checks(limit)

@router.get("/history/{gstin}", response_model=List[dict])
async def get_vendor_history(gstin: str):
    """Get compliance history for a specific vendor."""
    return check_crud.get_checks_by_gstin(gstin.strip().upper())

@router.get("/certificate/{check_id}")
async def download_certificate(check_id: int):
    """Download Due Diligence Certificate PDF."""
    try:
        check = check_crud.get_check_by_id(check_id)
        if not check:
            raise HTTPException(status_code=404, detail="Check not found")
        
        vendor_data = vendor_crud.get_cached_vendor(check["gstin"])
        filing_history = vendor_data.get("filing_history", []) if vendor_data else []
        registration_date = vendor_data.get("registration_date", "") if vendor_data else ""
        gst_status = vendor_data.get("gst_status", "") if vendor_data else ""
        
        rule_37a_status = "Clean"
        if check["decision"] == "STOP":
            rule_37a_status = "Failed"
        elif check["decision"] == "HOLD":
            rule_37a_status = "Review Required"
        
        check_data = {
            **check,
            "filing_history": filing_history,
            "registration_date": registration_date,
            "gst_status": gst_status,
            "rule_37a_status": rule_37a_status,
            "decision_reason": check.get("reason", "")
        }
        
        # Log data for debugging
        import logging
        logging.info(f"Generating PDF for check {check_id} with data keys: {check_data.keys()}")
        
        pdf_bytes = generate_certificate(check_data)
        
        # Verify PDF bytes
        if not pdf_bytes:
             raise Exception("PDF generation returned empty bytes")
             
        is_pdf = pdf_bytes.startswith(b"%PDF")
        media_type = "application/pdf" if is_pdf else "text/html"
        ext = "pdf" if is_pdf else "html"
        
        filename = f"TaxPayGuard_Cert_{check['gstin']}_{check_id}.{ext}"
        return Response(
            content=pdf_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        with open("/tmp/endpoint_error.log", "w") as f:
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())
            # Dump check data if available
            try:
                if 'check_data' in locals():
                    f.write(f"\nCheck Data: {str(check_data)}\n")
            except:
                pass
        print(f"Endpoint Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/test-scenarios")
async def test_scenarios():
    """Returns test GSTINs for demo purposes."""
    return {
        "message": "Use these GSTINs to test each decision rule",
        "scenarios": {
            "STOP - S1 (Cancelled)": "01AABCU9603R1ZX",
            "STOP - S2 (Suspended)": "02AABCU9603R1ZX", 
            "STOP - S3 (Non-Filer)": "03AABCU9603R1ZX",
            "HOLD - H1 (Late Filer)": "04AABCU9603R1ZX",
            "HOLD - H2 (New Vendor)": "05AABCU9603R1ZX",
            "HOLD - H3 (Name Mismatch)": "06AABCU9603R1ZX",
            "RELEASE - R1 (Compliant)": "33AABCU9603R1ZX"
        }
    }
