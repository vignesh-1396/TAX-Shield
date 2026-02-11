"""
Tests for decision engine
"""
import pytest
from app.services.decision import DecisionEngine

class TestDecisionEngine:
    """Test decision engine logic"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = DecisionEngine()
    
    def test_cancelled_vendor_stop(self):
        """Test that cancelled vendor returns STOP"""
        vendor_data = {
            "gst_status": "Cancelled",
            "legal_name": "TEST COMPANY",
            "filing_history": []
        }
        
        decision = self.engine.evaluate(vendor_data, amount=50000)
        
        assert decision["decision"] == "STOP"
        assert decision["risk_level"] == "HIGH"
        assert "cancelled" in decision["reason"].lower()
    
    def test_suspended_vendor_stop(self):
        """Test that suspended vendor returns STOP"""
        vendor_data = {
            "gst_status": "Suspended",
            "legal_name": "TEST COMPANY",
            "filing_history": []
        }
        
        decision = self.engine.evaluate(vendor_data, amount=50000)
        
        assert decision["decision"] == "STOP"
        assert decision["risk_level"] == "HIGH"
    
    def test_active_vendor_proceed(self):
        """Test that active vendor with good history returns PROCEED"""
        vendor_data = {
            "gst_status": "Active",
            "legal_name": "TEST COMPANY",
            "registration_date": "2020-01-15",
            "filing_history": [
                {"period": "Dec-2025", "status": "Filed", "filed_date": "2026-01-15"},
                {"period": "Nov-2025", "status": "Filed", "filed_date": "2025-12-15"},
            ]
        }
        
        decision = self.engine.evaluate(vendor_data, amount=50000)
        
        assert decision["decision"] == "PROCEED"
        assert decision["risk_level"] == "LOW"
    
    def test_non_filer_stop(self):
        """Test that non-filer returns STOP"""
        vendor_data = {
            "gst_status": "Active",
            "legal_name": "TEST COMPANY",
            "filing_history": [
                {"period": "Dec-2025", "status": "Not Filed"},
                {"period": "Nov-2025", "status": "Not Filed"},
            ]
        }
        
        decision = self.engine.evaluate(vendor_data, amount=50000)
        
        assert decision["decision"] == "STOP"
        assert "filing" in decision["reason"].lower()
    
    def test_new_vendor_hold(self):
        """Test that new vendor returns HOLD"""
        from datetime import datetime, timedelta
        recent_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        vendor_data = {
            "gst_status": "Active",
            "legal_name": "NEW COMPANY",
            "registration_date": recent_date,
            "filing_history": []
        }
        
        decision = self.engine.evaluate(vendor_data, amount=50000)
        
        assert decision["decision"] == "HOLD"
        assert decision["risk_level"] == "MEDIUM"
    
    def test_high_amount_threshold(self):
        """Test high amount threshold triggers additional checks"""
        vendor_data = {
            "gst_status": "Active",
            "legal_name": "TEST COMPANY",
            "registration_date": "2020-01-15",
            "filing_history": []
        }
        
        # High amount
        decision = self.engine.evaluate(vendor_data, amount=5000000)
        
        # Should be more conservative with high amounts
        assert decision["decision"] in ["HOLD", "STOP"]
