from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Dict, List, Any
import logging

from app.api.deps import get_current_user
from app.services.reconciliation import ReconciliationEngine
from app.utils.file_parser import parse_purchase_register
from app.db.crud import gstr2b_data

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", response_model=Dict[str, Any])
async def run_reconciliation(
    return_period: str = Form(..., description="Return period in MMYYYY format (e.g. 112024)"),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Run GSTR-2B Reconciliation.
    
    1. Upload Purchase Register (Excel/CSV)
    2. Fetch GSTR-2B data for the period
    3. Match invoices (Fuzzy Logic)
    4. Return detailed results
    """
    
    # Validate file type
    if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only .csv, .xlsx, .xls files are supported")
    
    try:
        # 1. Parse Purchase Register
        content = await file.read()
        pr_items, errors = parse_purchase_register(content, file.filename)
        
        if not pr_items:
            raise HTTPException(status_code=400, detail={"message": "No valid invoices found in file", "errors": errors[:5]})
        
        # 2. Fetch GSTR-2B Data
        gstr2b_items = gstr2b_data.get_invoices_by_period(current_user["id"], return_period)
        
        if not gstr2b_items:
            # Informative message if 2B data is missing but proceed with matching (which will result in all Missing in 2B)
            logger.warning(f"No GSTR-2B data found for period {return_period}. All items will be 'Missing in 2B'.")
            
        # 3. Run Matching Logic
        engine = ReconciliationEngine(tolerance=2.0) # Rs 2 tolerance
        results = engine.match_invoices(pr_items, gstr2b_items)
        
        # Calculate Summary Stats
        summary = {
            "total_pr": len(pr_items),
            "total_2b": len(gstr2b_items),
            "matched": len(results["matched"]),
            "mismatch": len(results["mismatch"]),
            "missing_in_2b": len(results["missing_in_2b"]),
            "missing_in_pr": len(results["missing_in_pr"]),
            "parse_errors": errors[:5] if errors else []
        }
        
        return {
            "summary": summary,
            "results": results,
            "period": return_period
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reconciliation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Reconciliation failed: {str(e)}")
