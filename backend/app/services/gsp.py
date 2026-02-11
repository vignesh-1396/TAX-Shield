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
from app.services.cache import cache

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
        self.access_token = None
        self.token_expiry = None

    def _get_access_token(self) -> Optional[str]:
        """Authenticate and get access token with Redis caching."""
        try:
            # Try Redis cache first
            cached_token = cache.get_gsp_token("sandbox")
            if cached_token:
                logger.debug("Using cached GSP token")
                return cached_token
            
            # Return in-memory cached token if valid (buffer of 5 minutes)
            if self.access_token and self.token_expiry:
                if datetime.now() < (self.token_expiry - timedelta(minutes=5)):
                    return self.access_token
            
            auth_url = f"{self.BASE_URL}/authenticate"
            headers = {
                "x-api-key": self.client_id,
                "x-api-secret": self.secret,
                "x-api-version": "1.0",
                "Content-Type": "application/json"
            }
            logger.info(f"Authenticating with GSP API at {auth_url}")
            response = requests.post(auth_url, headers=headers, timeout=10)
            response.raise_for_status()
            auth_data = response.json()
            logger.info(f"GSP Authentication Success. Token obtained.")
            
            self.access_token = auth_data.get("access_token")
            # Assume 1 hour validity if not provided, or parse from response if available
            # Sandbox typically returns 'expires_in' (seconds)
            expires_in = auth_data.get("expires_in", 3600) 
            self.token_expiry = datetime.now() + timedelta(seconds=int(expires_in))
            
            # Cache token in Redis
            cache.set_gsp_token("sandbox", self.access_token, expires_in - 300)  # 5 min buffer
            
            return self.access_token
        except Exception as e:
            logger.error(f"GSP Authentication Failed: {str(e)}")
            return None

    def get_filing_history(self, gstin: str, months: int = 3) -> List[Dict]:
        """
        Fetch GSTR-3B, GSTR-1, and IFF filing history for a vendor.
        
        Args:
            gstin: Vendor's GSTIN
            months: Number of months to analyze (default 3)
            
        Returns:
            List of filing records with period, filed_date, status, delay
        """
        try:
            # Step 1: Get access token
            token = self._get_access_token()
            if not token:
                logger.error("Failed to get access token for filing history")
                return []
            
            # Step 2: Call Track GST Returns API
            headers = {
                "authorization": token,
                "x-api-key": self.client_id,
                "x-api-version": "1.0.0",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            track_url = f"{self.BASE_URL}/gst/compliance/public/gstrs/track"
            
            # Get current financial year (Apr-Mar format)
            # For example: if current date is Feb 2026, FY is 2025-26
            from datetime import datetime
            current_date = datetime.now()
            if current_date.month >= 4:  # April or later
                fy_start = current_date.year
            else:  # Jan-Mar
                fy_start = current_date.year - 1
            financial_year = f"{fy_start}-{str(fy_start + 1)[-2:]}"  # e.g., "2025-26"
            
            # Add financial_year as query parameter
            track_url_with_params = f"{track_url}?financial_year={financial_year}"
            payload = {"gstin": gstin}
            
            logger.info(f"Fetching filing history for GSTIN: {gstin}, FY: {financial_year}")
            print(f"=== Track GST Returns Request ===")
            print(f"URL: {track_url_with_params}")
            print(f"Payload: {payload}")
            print(f"=================================")
            response = requests.post(track_url_with_params, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            response_json = response.json()
            
            print(f"=== Filing History API Response ===")
            print(f"Response: {response_json}")
            print(f"===================================")
            logger.info(f"Filing History API Response: {response_json}")
            
            # Step 3: Extract nested data (same structure as GSTIN search)
            outer_data = response_json.get("data", {})
            inner_data = outer_data.get("data", {}) if isinstance(outer_data, dict) else {}
            filed_list = inner_data.get("EFiledlist", [])
            
            if not filed_list:
                logger.warning(f"No filing history found for GSTIN: {gstin}")
                return []
            
            # Step 4: Process and format filing records
            filing_records = []
            
            for record in filed_list:
                rtn_type = record.get("rtntype", "")
                
                # Only include GSTR-3B, GSTR-1, and IFF
                if rtn_type not in ["GSTR3B", "GSTR1", "IFF"]:
                    continue
                
                # Parse return period (MMYYYY format)
                ret_period = record.get("ret_prd", "")
                if len(ret_period) == 6:
                    month = ret_period[:2]
                    year = ret_period[2:]
                    period_display = f"{month}/{year}"
                else:
                    period_display = ret_period
                
                # Get filing details
                filed_date = record.get("dof", "N/A")
                status = record.get("status", "Unknown")
                
                # Determine delay status (simplified - can be enhanced later)
                delay = "On Time" if status == "Filed" else "Late"
                
                filing_records.append({
                    "period": period_display,
                    "filed_date": filed_date,
                    "status": status,
                    "delay": delay,
                    "return_type": rtn_type
                })
            
            # Sort by period (most recent first) and limit to requested months
            filing_records.sort(key=lambda x: x["period"], reverse=True)
            
            # Return up to months * 2 records (GSTR-1 + GSTR-3B per month)
            return filing_records[:months * 2]
            
        except requests.exceptions.HTTPError as e:
            # Log the actual error response for debugging
            error_response = e.response.text if hasattr(e.response, 'text') else str(e)
            logger.error(f"HTTP Error fetching filing history: Status {e.response.status_code}, Response: {error_response}")
            print(f"=== Filing History API Error ===")
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {error_response}")
            print(f"================================")
            return []
        except Exception as e:
            logger.error(f"Error fetching filing history from Sandbox GSP: {str(e)}")
            return []

    def get_vendor_data(self, gstin: str) -> Optional[Dict]:
        """Fetch real data from Sandbox.co.in with Redis caching"""
        try:
            # Check cache first
            cached_data = cache.get_vendor_data(gstin)
            if cached_data:
                logger.info(f"Cache HIT for vendor: {gstin}")
                return cached_data
            
            logger.info(f"Cache MISS for vendor: {gstin}. Fetching from GSP...")
            
            # Step 1: Get Access Token
            token = self._get_access_token()
            if not token:
                logger.error("Failed to obtain GSP access token")
                return None

            headers = {
                "authorization": token,  # No "Bearer" prefix per Sandbox docs
                "x-api-key": self.client_id,
                "x-api-version": "1.0.0",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Step 2: Get GST details using verified endpoint
            # Endpoint: POST /gst/compliance/public/gstin/search
            gst_url = f"{self.BASE_URL}/gst/compliance/public/gstin/search"
            payload = {"gstin": gstin}
            
            response = requests.post(gst_url, json=payload, headers=headers, timeout=10)
            
            # Handle 403 specifically to warn user
            if response.status_code == 403:
                logger.error(f"GSP Permission Denied: {response.text}")
                # Return a special mock indicating permission issue? 
                # Or just None for now.
                return None
            
            response.raise_for_status()
            response_json = response.json()
            
            # Log the full response for debugging
            print(f"=== GSP API Full Response ===")
            print(f"Response: {response_json}")
            print(f"=============================")
            logger.info(f"GSP API Response: {response_json}")
            
            # Sandbox API has nested data structure: response.data.data
            outer_data = response_json.get("data", {})
            
            if not outer_data:
                logger.warning(f"No outer data returned from GSP for GSTIN: {gstin}")
                return None
            
            # The actual GSTIN details are in the nested 'data' field
            # Structure: {"code": 200, "data": {"data": {...actual fields...}}}
            inner_data = outer_data.get("data", {}) if isinstance(outer_data, dict) else {}
            
            # If inner_data is empty, try using outer_data directly (fallback)
            data = inner_data if inner_data else outer_data
            
            if not data:
                logger.warning(f"No inner data returned from GSP for GSTIN: {gstin}")
                return None

            # Step 3: Get Filing History from Track GST Returns API
            filing_data = self.get_filing_history(gstin, months=3)
            logger.info(f"Retrieved {len(filing_data)} filing records for GSTIN: {gstin}")

            # Map to our internal schema
            vendor_data = {
                "gstin": gstin,
                "gst_status": data.get("sts") or data.get("status") or "Active",
                "registration_date": data.get("rgdt") or data.get("registration_date") or "N/A",
                "legal_name": data.get("lgnm") or data.get("legal_name") or "Unknown",
                "trade_name": data.get("tradeNam") or data.get("trade_name") or data.get("lgnm") or "Unknown",
                "filing_history": filing_data,
                "last_updated": datetime.now().isoformat(),
                "source": "GSP_LIVE"
            }
            
            # Cache the vendor data for 24 hours
            cache.set_vendor_data(gstin, vendor_data)
            logger.info(f"Cached vendor data for: {gstin}")
            
            return vendor_data
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
