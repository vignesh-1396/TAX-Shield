"""
Input Validation and Sanitization Utilities
"""
import re
from typing import Optional
import html
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates and sanitizes user inputs"""
    
    # GSTIN format: 2 digits + 10 alphanumeric + 1 letter + 1 digit + 1 letter + 1 alphanumeric
    GSTIN_PATTERN = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
    
    # PAN format: 5 letters + 4 digits + 1 letter
    PAN_PATTERN = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
    
    # Email pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_gstin(gstin: str) -> tuple[bool, Optional[str]]:
        """
        Validate GSTIN format
        
        Returns:
            (is_valid, error_message)
        """
        if not gstin:
            return False, "GSTIN is required"
        
        gstin = gstin.strip().upper()
        
        if len(gstin) != 15:
            return False, "GSTIN must be exactly 15 characters"
        
        if not InputValidator.GSTIN_PATTERN.match(gstin):
            return False, "Invalid GSTIN format"
        
        return True, None
    
    @staticmethod
    def validate_amount(amount: float) -> tuple[bool, Optional[str]]:
        """Validate transaction amount"""
        if amount is None:
            return False, "Amount is required"
        
        if amount <= 0:
            return False, "Amount must be positive"
        
        if amount > 999999999:  # 99 crores
            return False, "Amount exceeds maximum limit"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, Optional[str]]:
        """Validate email format"""
        if not email:
            return False, "Email is required"
        
        if not InputValidator.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        if len(email) > 255:
            return False, "Email too long"
        
        return True, None
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        Sanitize string input
        - HTML escape
        - Trim whitespace
        - Limit length
        """
        if not text:
            return ""
        
        # HTML escape to prevent XSS
        sanitized = html.escape(text.strip())
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, Optional[str]]:
        """
        Validate filename for security (prevent path traversal).
        
        Args:
            filename: Filename to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename cannot be empty"
        
        # Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            return False, "Filename cannot contain path separators or '..' (path traversal attempt)"
        
        # Check for valid characters (alphanumeric, dash, underscore, dot)
        import re
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
            return False, "Filename contains invalid characters"
        
        # Check file extension is allowed
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.pdf', '.zip']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            return False, f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength
        - Minimum 8 characters
        - At least one uppercase
        - At least one lowercase
        - At least one digit
        - At least one special character
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 128:
            return False, "Password too long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, None


# Singleton instance
validator = InputValidator()
