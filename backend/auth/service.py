"""
TaxPay Guard - Auth Service
Business logic for user authentication
"""
import os
import uuid
from datetime import datetime
from typing import Optional, Dict
from passlib.context import CryptContext

# Import shared database layer (supports both SQLite and PostgreSQL)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_connection, _ph, _row_to_dict
from .jwt_handler import create_access_token

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_user(email: str, password: str, name: str, company_name: str = None) -> Dict:
    """
    Create a new user account.
    
    Args:
        email: User's email address
        password: Plain text password (will be hashed)
        name: User's full name
        company_name: Optional company name
        
    Returns:
        Dict with user data (excluding password)
        
    Raises:
        ValueError: If email already exists
    """
    with get_connection() as (conn, cursor):
        # Check if email exists
        cursor.execute(f"SELECT id FROM users WHERE email = {_ph()}", (email.lower(),))
        if cursor.fetchone():
            raise ValueError("Email already registered")
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        created_at = datetime.now().isoformat()
        
        cursor.execute(f"""
            INSERT INTO users (id, email, password_hash, name, company_name, role, is_active, created_at)
            VALUES ({_ph(8)})
        """, (user_id, email.lower(), password_hash, name, company_name, 'user', 1, created_at))
        
        conn.commit()
    
    return {
        "id": user_id,
        "email": email.lower(),
        "name": name,
        "company_name": company_name,
        "role": "user",
        "created_at": created_at
    }


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """
    Authenticate user with email and password.
    
    Args:
        email: User's email
        password: Plain text password
        
    Returns:
        User dict if valid, None if invalid credentials
    """
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            SELECT id, email, password_hash, name, company_name, role, is_active, created_at
            FROM users WHERE email = {_ph()}
        """, (email.lower(),))
        
        row = cursor.fetchone()
    
    if not row:
        return None
    
    user = _row_to_dict(row)
    
    # Check if user is active
    if not user.get("is_active"):
        return None
    
    # Verify password
    if not verify_password(password, user["password_hash"]):
        return None
    
    # Update last login
    with get_connection() as (conn, cursor):
        cursor.execute(
            f"UPDATE users SET last_login = {_ph()} WHERE id = {_ph()}",
            (datetime.now().isoformat(), user["id"])
        )
        conn.commit()
    
    # Remove password hash from response
    del user["password_hash"]
    return user


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            SELECT id, email, name, company_name, role, created_at
            FROM users WHERE id = {_ph()} AND is_active = 1
        """, (user_id,))
        
        row = cursor.fetchone()
    
    return _row_to_dict(row)


def login_user(email: str, password: str) -> Optional[Dict]:
    """
    Login user and return token response.
    
    Returns:
        Dict with access_token and user data, or None if invalid
    """
    user = authenticate_user(email, password)
    
    if not user:
        return None
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user["id"], "email": user["email"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "user": user
    }
