"""
Tests for input validation utilities
"""
import pytest
from app.utils.validation import validator

class TestInputValidation:
    """Test input validation functions"""
    
    def test_valid_gstin(self):
        """Test valid GSTIN validation"""
        valid_gstins = [
            "27AABCU9603R1ZM",
            "29AABCT1332L1ZV",
            "07AAGFF2194N1Z1"
        ]
        
        for gstin in valid_gstins:
            is_valid, error = validator.validate_gstin(gstin)
            assert is_valid, f"GSTIN {gstin} should be valid, got error: {error}"
            assert error is None
    
    def test_invalid_gstin_length(self):
        """Test GSTIN with invalid length"""
        is_valid, error = validator.validate_gstin("27AABCU9603")
        assert not is_valid
        assert "15 characters" in error
    
    def test_invalid_gstin_format(self):
        """Test GSTIN with invalid format"""
        invalid_gstins = [
            "AAAAAAAAAAAAAA",  # All letters
            "12345678901234",   # All numbers
            "27AABCU9603R1ZZ",  # Invalid checksum character
        ]
        
        for gstin in invalid_gstins:
            is_valid, error = validator.validate_gstin(gstin)
            assert not is_valid, f"GSTIN {gstin} should be invalid"
    
    def test_valid_amount(self):
        """Test valid amount validation"""
        valid_amounts = [100, 1000.50, 999999.99]
        
        for amount in valid_amounts:
            is_valid, error = validator.validate_amount(amount)
            assert is_valid, f"Amount {amount} should be valid"
            assert error is None
    
    def test_invalid_amount_negative(self):
        """Test negative amount"""
        is_valid, error = validator.validate_amount(-100)
        assert not is_valid
        assert "positive" in error.lower()
    
    def test_invalid_amount_zero(self):
        """Test zero amount"""
        is_valid, error = validator.validate_amount(0)
        assert not is_valid
        assert "positive" in error.lower()
    
    def test_invalid_amount_too_large(self):
        """Test amount exceeding maximum"""
        is_valid, error = validator.validate_amount(100000000)  # 10 crore
        assert not is_valid
        assert "maximum" in error.lower()
    
    def test_valid_email(self):
        """Test valid email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.in",
            "admin+tag@company.org"
        ]
        
        for email in valid_emails:
            is_valid, error = validator.validate_email(email)
            assert is_valid, f"Email {email} should be valid"
    
    def test_invalid_email(self):
        """Test invalid email validation"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com"
        ]
        
        for email in invalid_emails:
            is_valid, error = validator.validate_email(email)
            assert not is_valid, f"Email {email} should be invalid"
    
    def test_valid_password(self):
        """Test valid password validation"""
        valid_passwords = [
            "Test@1234",
            "SecureP@ssw0rd",
            "MyP@ssw0rd123"
        ]
        
        for password in valid_passwords:
            is_valid, error = validator.validate_password(password)
            assert is_valid, f"Password should be valid, got error: {error}"
    
    def test_invalid_password_too_short(self):
        """Test password too short"""
        is_valid, error = validator.validate_password("Test@1")
        assert not is_valid
        assert "8 characters" in error
    
    def test_invalid_password_no_uppercase(self):
        """Test password without uppercase"""
        is_valid, error = validator.validate_password("test@1234")
        assert not is_valid
        assert "uppercase" in error.lower()
    
    def test_invalid_password_no_lowercase(self):
        """Test password without lowercase"""
        is_valid, error = validator.validate_password("TEST@1234")
        assert not is_valid
        assert "lowercase" in error.lower()
    
    def test_invalid_password_no_digit(self):
        """Test password without digit"""
        is_valid, error = validator.validate_password("Test@Password")
        assert not is_valid
        assert "digit" in error.lower()
    
    def test_invalid_password_no_special(self):
        """Test password without special character"""
        is_valid, error = validator.validate_password("Test1234")
        assert not is_valid
        assert "special" in error.lower()
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        dangerous_input = "<script>alert('XSS')</script>"
        sanitized = validator.sanitize_string(dangerous_input)
        
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
    
    def test_sanitize_string_max_length(self):
        """Test string sanitization with max length"""
        long_string = "a" * 2000
        sanitized = validator.sanitize_string(long_string, max_length=100)
        
        assert len(sanitized) <= 100
    
    def test_valid_filename(self):
        """Test valid filename validation"""
        valid_filenames = [
            "document.pdf",
            "batch_upload.csv",
            "report-2024.xlsx"
        ]
        
        for filename in valid_filenames:
            is_valid, error = validator.validate_filename(filename)
            assert is_valid, f"Filename {filename} should be valid"
    
    def test_invalid_filename_path_traversal(self):
        """Test filename with path traversal attempt"""
        invalid_filenames = [
            "../etc/passwd",
            "..\\windows\\system32",
            "../../secret.txt"
        ]
        
        for filename in invalid_filenames:
            is_valid, error = validator.validate_filename(filename)
            assert not is_valid, f"Filename {filename} should be invalid"
            assert "path" in error.lower()
