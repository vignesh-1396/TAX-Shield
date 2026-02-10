import uuid
from datetime import datetime
from typing import Optional, Dict
from app.db.session import get_connection, ph, row_to_dict

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"SELECT * FROM users WHERE email = {ph()}", (email.lower(),))
        row = cursor.fetchone()
    return row_to_dict(row)

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            SELECT id, email, name, company_name, role, created_at, is_active
            FROM users WHERE id = {ph()}
        """, (user_id,))
        row = cursor.fetchone()
    return row_to_dict(row)

def create_user(email: str, password_hash: str, name: str, company_name: str = None) -> Dict:
    """Create a new user"""
    user_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            INSERT INTO users (id, email, password_hash, name, company_name, role, is_active, created_at)
            VALUES ({ph(8)})
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

def update_last_login(user_id: str):
    """Update last login timestamp"""
    with get_connection() as (conn, cursor):
        cursor.execute(
            f"UPDATE users SET last_login = {ph()} WHERE id = {ph()}",
            (datetime.now().isoformat(), user_id)
        )
        conn.commit()
