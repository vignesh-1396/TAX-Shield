"""
ITC Shield - Mock GSP Data Provider
Simulates GST Suvidha Provider API responses for testing
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import random

class MockGSPProvider:
    """
    Simulates GSP API responses for different vendor scenarios.
    In production, replace with real GSP API calls (Masters India, Vayana, etc.)
    """
    
    # Predefined test scenarios based on GSTIN patterns
    SCENARIOS = {
        # STOP scenarios (S1, S2, S3)
        "CANCELLED": {
            "gst_status": "Cancelled",
            "registration_date": "2020-01-15",
            "legal_name": "CANCELLED TRADERS PVT LTD",
            "trade_name": "CANCELLED TRADERS",
            "filing_history": []
        },
        "SUSPENDED": {
            "gst_status": "Suspended",
            "registration_date": "2019-06-20",
            "legal_name": "SUSPENDED INDUSTRIES LTD",
            "trade_name": "SUSPENDED IND",
            "filing_history": [
                {"period": "Dec-2025", "status": "Not Filed", "filed_date": None},
                {"period": "Nov-2025", "status": "Not Filed", "filed_date": None},
            ]
        },
        "NON_FILER": {
            "gst_status": "Active",
            "registration_date": "2018-04-01",
            "legal_name": "NON FILER ENTERPRISES",
            "trade_name": "NFE",
            "filing_history": [
                {"period": "Dec-2025", "status": "Not Filed", "filed_date": None},
                {"period": "Nov-2025", "status": "Not Filed", "filed_date": None},
                {"period": "Oct-2025", "status": "Filed", "filed_date": "2025-11-18"},
            ]
        },
        # HOLD scenarios (H1, H2, H3)
        "LATE_FILER": {
            "gst_status": "Active",
            "registration_date": "2017-07-01",
            "legal_name": "LATE FILER COMPANY",
            "trade_name": "LFC",
            "filing_history": [
                {"period": "Dec-2025", "status": "Filed", "filed_date": "2026-02-15"},  # 45 days late
                {"period": "Nov-2025", "status": "Filed", "filed_date": "2025-12-20"},
                {"period": "Oct-2025", "status": "Filed", "filed_date": "2025-11-20"},
            ]
        },
        "NEW_VENDOR": {
            "gst_status": "Active",
            "registration_date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),  # 3 months old
            "legal_name": "NEW STARTUP PRIVATE LIMITED",
            "trade_name": "NEW STARTUP",
            "filing_history": [
                {"period": "Dec-2025", "status": "Filed", "filed_date": "2026-01-18"},
                {"period": "Nov-2025", "status": "Filed", "filed_date": "2025-12-18"},
            ]
        },
        "NAME_MISMATCH": {
            "gst_status": "Active",
            "registration_date": "2019-01-01",
            "legal_name": "ALPHA BETA GAMMA DELTA INDUSTRIES PRIVATE LIMITED",
            "trade_name": "XYZ TRADERS",  # Completely different
            "filing_history": [
                {"period": "Dec-2025", "status": "Filed", "filed_date": "2026-01-18"},
                {"period": "Nov-2025", "status": "Filed", "filed_date": "2025-12-18"},
                {"period": "Oct-2025", "status": "Filed", "filed_date": "2025-11-18"},
            ]
        },
        # RELEASE scenario (R1)
        "COMPLIANT": {
            "gst_status": "Active",
            "registration_date": "2018-01-01",
            "legal_name": "GOOD VENDOR PRIVATE LIMITED",
            "trade_name": "GOOD VENDOR PVT LTD",
            "filing_history": [
                {"period": "Dec-2025", "status": "Filed", "filed_date": "2026-01-18"},
                {"period": "Nov-2025", "status": "Filed", "filed_date": "2025-12-18"},
                {"period": "Oct-2025", "status": "Filed", "filed_date": "2025-11-18"},
            ]
        }
    }
    
    @classmethod
    def get_vendor_data(cls, gstin: str) -> Dict:
        """
        Fetch vendor data based on GSTIN.
        Uses GSTIN patterns to return different test scenarios.
        """
        # Validate GSTIN format (basic check)
        if not gstin or len(gstin) != 15:
            return None
        
        # Determine scenario based on GSTIN state code (first 2 digits)
        state_code = gstin[:2]
        
        # Map state codes to scenarios for testing
        scenario_map = {
            "01": "CANCELLED",      # Jammu & Kashmir
            "02": "SUSPENDED",      # Himachal Pradesh
            "03": "NON_FILER",      # Punjab
            "04": "LATE_FILER",     # Chandigarh
            "05": "NEW_VENDOR",     # Uttarakhand
            "06": "NAME_MISMATCH",  # Haryana
            # All other state codes return COMPLIANT
        }
        
        scenario_name = scenario_map.get(state_code, "COMPLIANT")
        scenario = cls.SCENARIOS[scenario_name].copy()
        
        # Add dynamic data
        scenario["gstin"] = gstin
        scenario["last_updated"] = datetime.now().isoformat()
        scenario["source"] = "MOCK_GSP"
        
        return scenario
    
    @classmethod
    def get_filing_due_date(cls, period: str) -> datetime:
        """Get the due date for GSTR-3B filing (20th of next month)"""
        # Parse period like "Dec-2025"
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                     "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        
        parts = period.split("-")
        month = month_map.get(parts[0], 1)
        year = int(parts[1])
        
        # Due date is 20th of next month
        if month == 12:
            return datetime(year + 1, 1, 20)
        else:
            return datetime(year, month + 1, 20)
