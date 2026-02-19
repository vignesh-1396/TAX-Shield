from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from app.db.crud import check as check_crud

router = APIRouter()

@router.get("/summary")
async def get_compliance_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get compliance summary statistics for a date range.
    If no dates provided, returns last 30 days.
    """
    # Default to last 30 days if no dates provided
    if not start_date and not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        summary = check_crud.get_checks_summary(start_date, end_date)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.get("/high-risk")
async def get_high_risk_vendors(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get all HOLD and STOP vendors for a date range.
    If no dates provided, returns last 30 days.
    """
    # Default to last 30 days if no dates provided
    if not start_date and not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        high_risk_checks = check_crud.get_high_risk_checks(start_date, end_date)
        
        # Calculate total exposure
        total_exposure = sum(check.get('amount', 0) for check in high_risk_checks)
        
        return {
            "total_count": len(high_risk_checks),
            "total_exposure": total_exposure,
            "checks": high_risk_checks,
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate high-risk report: {str(e)}")


@router.get("/audit-trail")
async def get_audit_trail(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(1000, description="Maximum number of records")
):
    """
    Get complete audit trail of all compliance checks for a date range.
    If no dates provided, returns last 30 days.
    """
    # Default to last 30 days if no dates provided
    if not start_date and not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        checks = check_crud.get_checks_by_date_range(start_date, end_date, limit)
        
        return {
            "total_count": len(checks),
            "checks": checks,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate audit trail: {str(e)}")
