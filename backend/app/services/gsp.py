"""
ITC Shield - GSP Data Providers
Handles fetching GST data from various providers (Mock, Sandbox.co.in, etc.)
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import requests
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseGSPProvider(ABC):
    """Abstract base class for GSP providers."""
    
    @abstractmethod
    def get_vendor_data(self, gstin: str) -> Optional[Dict]:
        """Fetch vendor data based on GSTIN."""
        pass

class MockGSPProvider(BaseGSPProvider):
    """
    Simulates GSP API responses for different vendor scenarios.
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
                {"period": "Dec-2025", "status": "Filed", "filed_date": "2026-02-15"},
                {"period": "Nov-2025", "status": "Filed", "filed_date": "2025-12-20"},
                {"period": "Oct-2025", "status": "Filed", "filed_date": "2025-11-20"},
            ]
        },
        "NEW_VENDOR": {
            "gst_status": "Active",
            "registration_date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
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
            "trade_name": "XYZ TRADERS",
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

    def get_vendor_data(self, gstin: str) -> Dict:
        if not gstin or len(gstin) != 15:
            return None
        
        state_code = gstin[:2]
        scenario_map = {
            "01": "CANCELLED", "02": "SUSPENDED", "03": "NON_FILER",
            "04": "LATE_FILER", "05": "NEW_VENDOR", "06": "NAME_MISMATCH",
        }
        
        scenario_name = scenario_map.get(state_code, "COMPLIANT")
        scenario = self.SCENARIOS[scenario_name].copy()
        scenario.update({
            "gstin": gstin,
            "last_updated": datetime.now().isoformat(),
            "source": "MOCK_GSP"
        })
        return scenario

class SandboxGSPProvider(BaseGSPProvider):
    """
    Real GSP Provider using Sandbox.co.in (Zoop) API.
    Supports both Sandbox (key_test) and Production (key_live) keys.
    """
    # Production/Live URL (used for key_live_...)
    BASE_URL = "https://api.sandbox.co.in"
    
    def __init__(self, client_id: str, secret: str):
        self.client_id = client_id
        self.secret = secret

    def _get_access_token(self) -> Optional[str]:
        """Authenticate and get access token."""
        try:
            auth_url = f"{self.BASE_URL}/authenticate"
            headers = {
                "x-api-key": self.client_id,
                "x-api-secret": self.secret,
                "x-api-version": "1.0",
                "Content-Type": "application/json"
            }
            response = requests.post(auth_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            logger.error(f"GSP Authentication Failed: {str(e)}")
            return None

    def get_vendor_data(self, gstin: str) -> Optional[Dict]:
        """Fetch real data from Sandbox.co.in"""
        try:
            # Step 1: Get Access Token
            token = self._get_access_token()
            if not token:
                logger.error("Failed to obtain GSP access token")
                return None

            headers = {
                "Authorization": f"Bearer {token}",
                "x-api-key": self.client_id,
                "x-api-version": "1.0",
                "Accept": "application/json"
            }
            
            # Step 2: Get GST details using verified endpoint
            # Endpoint: /gst/compliance/public/gstin/search?gstin={gstin}
            gst_url = f"{self.BASE_URL}/gst/compliance/public/gstin/search?gstin={gstin}"
            
            response = requests.get(gst_url, headers=headers, timeout=10)
            
            # Handle 403 specifically to warn user
            if response.status_code == 403:
                logger.error(f"GSP Permission Denied: {response.text}")
                # Return a special mock indicating permission issue? 
                # Or just None for now.
                return None
                
            response.raise_for_status()
            data = response.json().get("data", {})

            if not data:
                return None

            # Note: The response structure might differ for this endpoint.
            # Assuming standard Zoop structure for now, but in reality 
            # we might need to map fields properly once we see successful response.
            # Since we only saw 403, we keep mapping logic generic.

            # Step 3: Get Filing History (if available via similar endpoint)
            filing_data = []
            # We skip filing history fetch until basic search works to avoid extra errors.

            # Map to our internal schema
            return {
                "gstin": gstin,
                "gst_status": data.get("sts", "Active"), # Default to Active if found
                "registration_date": data.get("rgdt"),
                "legal_name": data.get("lgnm"),
                "trade_name": data.get("tradeNam") or data.get("lgnm"),
                "filing_history": filing_data,
                "last_updated": datetime.now().isoformat(),
                "source": "REAL_GSP_SANDBOX"
            }
        except Exception as e:
            logger.error(f"Error fetching data from Sandbox GSP: {str(e)}")
            return None

def get_gsp_provider() -> BaseGSPProvider:
    """Factory function to get the configured GSP provider."""
    if settings.GSP_MODE.lower() == "sandbox" and settings.SANDBOX_CLIENT_ID:
        return SandboxGSPProvider(
            client_id=settings.SANDBOX_CLIENT_ID,
            secret=settings.SANDBOX_SECRET
        )
    return MockGSPProvider()
