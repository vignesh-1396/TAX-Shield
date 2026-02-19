"""
ITC Shield - Decision Engine
Implements all 7 decision rules (S1-S3, H1-H3, R1) per decision_logic.md
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple
from difflib import SequenceMatcher

class DecisionEngine:
    """
    Risk Decision Engine implementing STOP/HOLD/RELEASE logic
    Based on GST Rule 37A compliance requirements
    """
    
    # Decision constants
    STOP = "STOP"
    HOLD = "HOLD"  
    RELEASE = "RELEASE"
    
    # Risk levels
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    
    def check_vendor(self, vendor_data: Dict, amount: float = 0) -> Dict:
        """
        Main entry point for vendor compliance check.
        
        Args:
            vendor_data: Dict containing GST data from GSP
            amount: Transaction amount (for future TDS checks)
            
        Returns:
            Dict with decision, rule_id, reason, risk_level, timestamp
        """
        timestamp = datetime.now()
        
        if not vendor_data:
            return self._create_result(
                self.STOP, "S0", 
                "Unable to fetch vendor data. Verification failed.",
                self.CRITICAL, timestamp
            )
        
        # Apply rules in priority order
        # STOP rules first (S1, S2, S3)
        result = self._check_stop_rules(vendor_data, timestamp)
        if result:
            return result
            
        # HOLD rules next (H1, H2, H3)
        result = self._check_hold_rules(vendor_data, timestamp)
        if result:
            return result
            
        # Default: RELEASE (R1)
        return self._create_result(
            self.RELEASE, "R1",
            "Vendor is compliant. Safe to process payment.",
            self.LOW, timestamp
        )
    
    def _check_stop_rules(self, data: Dict, timestamp: datetime) -> Dict:
        """Check S1, S2, S3 rules"""
        
        gst_status = data.get("gst_status", "").lower()
        
        # S1: GST Status = Cancelled
        if gst_status == "cancelled":
            return self._create_result(
                self.STOP, "S1",
                "Vendor's GST registration has been CANCELLED. ITC claim will be rejected under Section 16(2)(c).",
                self.CRITICAL, timestamp
            )
        
        # S2: GST Status = Suspended
        if gst_status == "suspended":
            return self._create_result(
                self.STOP, "S2",
                "Vendor's GST registration is SUSPENDED by authorities. Payment blocked per Rule 37A.",
                self.CRITICAL, timestamp
            )
        
        # S3: GSTR-3B not filed for 2+ consecutive periods
        filing_history = data.get("filing_history", [])
        if len(filing_history) >= 2:
            not_filed_count = 0
            for filing in filing_history[:2]:  # Last 2 periods
                if filing.get("status") == "Not Filed":
                    not_filed_count += 1
            
            if not_filed_count >= 2:
                return self._create_result(
                    self.STOP, "S3",
                    "Vendor has NOT filed GSTR-3B for 2+ consecutive months. ITC reversal risk is HIGH under Rule 37A.",
                    self.CRITICAL, timestamp
                )
        
        return None
    
    def _check_hold_rules(self, data: Dict, timestamp: datetime) -> Dict:
        """Check H1, H2, H3 rules"""
        
        filing_history = data.get("filing_history", [])
        
        # H1: GSTR-3B filed but delayed by 30+ days
        if filing_history:
            latest = filing_history[0]
            if latest.get("status") == "Filed" and latest.get("filed_date"):
                delay_days = self._calculate_filing_delay(
                    latest.get("period"), 
                    latest.get("filed_date")
                )
                if delay_days >= 30:
                    return self._create_result(
                        self.HOLD, "H1",
                        f"Vendor files returns LATE (delayed by {delay_days} days). Recommend CFO review before releasing payment.",
                        self.HIGH, timestamp
                    )
        
        # H2: GST registration less than 6 months old
        reg_date_str = data.get("registration_date")
        if reg_date_str:
            try:
                reg_date = datetime.strptime(reg_date_str, "%Y-%m-%d")
                months_old = (timestamp - reg_date).days / 30
                if months_old < 6:
                    return self._create_result(
                        self.HOLD, "H2",
                        f"NEW VENDOR - Registration is only {int(months_old)} months old. Limited compliance history available.",
                        self.MEDIUM, timestamp
                    )
            except ValueError:
                pass
        
        # H3: Legal Name vs Trade Name mismatch (>30% difference)
        legal_name = data.get("legal_name", "")
        trade_name = data.get("trade_name", "")
        
        if legal_name and trade_name:
            similarity = self._calculate_name_similarity(legal_name, trade_name)
            if similarity < 0.7:  # Less than 70% similar = more than 30% different
                return self._create_result(
                    self.HOLD, "H3",
                    f"NAME MISMATCH detected. Legal: '{legal_name}' vs Trade: '{trade_name}'. Verify vendor identity before payment.",
                    self.MEDIUM, timestamp
                )
        
        return None
    
    def _calculate_filing_delay(self, period: str, filed_date: str) -> int:
        """Calculate days of delay in filing"""
        try:
            # Parse period like "Dec-2025"
            month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
            
            parts = period.split("-")
            month = month_map.get(parts[0], 1)
            year = int(parts[1])
            
            # Due date is 20th of next month
            if month == 12:
                due_date = datetime(year + 1, 1, 20)
            else:
                due_date = datetime(year, month + 1, 20)
            
            # Parse filed date
            filed = datetime.strptime(filed_date, "%Y-%m-%d")
            
            delay = (filed - due_date).days
            return max(0, delay)
            
        except (ValueError, KeyError, IndexError):
            return 0
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity ratio between two names"""
        # Normalize names
        n1 = name1.upper().replace("PVT", "PRIVATE").replace("LTD", "LIMITED")
        n2 = name2.upper().replace("PVT", "PRIVATE").replace("LTD", "LIMITED")
        
        return SequenceMatcher(None, n1, n2).ratio()
    
    def _create_result(self, decision: str, rule_id: str, reason: str, 
                      risk_level: str, timestamp: datetime) -> Dict:
        """Create standardized result dictionary"""
        return {
            "decision": decision,
            "rule_id": rule_id,
            "reason": reason,
            "risk_level": risk_level,
            "timestamp": timestamp.isoformat(),
            "timestamp_display": timestamp.strftime("%d-%b-%Y %H:%M:%S IST")
        }


# Singleton instance
engine = DecisionEngine()

def check_vendor(vendor_data: Dict, amount: float = 0) -> Dict:
    """Convenience function for vendor check"""
    return engine.check_vendor(vendor_data, amount)
