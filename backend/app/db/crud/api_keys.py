"""
API Key Management - CRUD Operations
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from app.db.session import get_connection
import logging

logger = logging.getLogger(__name__)


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a secure API key
    
    Returns:
        tuple: (full_key, hashed_key, prefix)
        - full_key: The actual key to show user (only shown once)
        - hashed_key: Hashed version to store in database
        - prefix: First 8 chars for identification
    """
    # Generate secure random key
    full_key = f"itcs_{secrets.token_urlsafe(32)}"
    
    # Create hash for storage
    hashed_key = hashlib.sha256(full_key.encode()).hexdigest()
    
    # Get prefix for display
    prefix = full_key[:12]  # itcs_XXXXXXX
    
    return full_key, hashed_key, prefix


def create_api_key(
    user_id: str,
    key_name: str,
    expires_in_days: Optional[int] = None,
    permissions: str = "read,write"
) -> Dict[str, Any]:
    """
    Create a new API key for a user
    
    Args:
        user_id: User ID
        key_name: Descriptive name for the key
        expires_in_days: Optional expiration in days
        permissions: Comma-separated permissions
        
    Returns:
        dict with key details (includes full key - only shown once!)
    """
    import uuid
    
    # Generate key
    full_key, hashed_key, prefix = generate_api_key()
    
    # Calculate expiration
    expires_at = None
    if expires_in_days:
        expires_at = datetime.now() + timedelta(days=expires_in_days)
    
    key_id = str(uuid.uuid4())
    
    with get_connection() as (conn, cursor):
        cursor.execute("""
            INSERT INTO api_keys (
                id, user_id, key_name, api_key, key_prefix,
                expires_at, permissions
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            key_id, user_id, key_name, hashed_key, prefix,
            expires_at, permissions
        ))
        conn.commit()
    
    logger.info(f"API key created: {prefix}... for user {user_id}")
    
    return {
        "id": key_id,
        "key_name": key_name,
        "api_key": full_key,  # ONLY TIME THIS IS RETURNED!
        "prefix": prefix,
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "permissions": permissions
    }


def get_user_api_keys(user_id: str) -> List[Dict[str, Any]]:
    """Get all API keys for a user (without the actual keys)"""
    with get_connection() as (conn, cursor):
        cursor.execute("""
            SELECT 
                id, key_name, key_prefix, created_at, last_used_at,
                expires_at, is_active, permissions, usage_count
            FROM api_keys
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        keys = []
        for row in cursor.fetchall():
            keys.append({
                "id": row[0],
                "key_name": row[1],
                "prefix": row[2],
                "created_at": row[3],
                "last_used_at": row[4],
                "expires_at": row[5],
                "is_active": bool(row[6]),
                "permissions": row[7],
                "usage_count": row[8]
            })
        
        return keys


def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Validate an API key and return user info if valid
    
    Args:
        api_key: The full API key from request
        
    Returns:
        dict with user_id and permissions if valid, None otherwise
    """
    # Hash the provided key
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    
    with get_connection() as (conn, cursor):
        cursor.execute("""
            SELECT 
                ak.id, ak.user_id, ak.permissions, ak.expires_at,
                u.email, u.name
            FROM api_keys ak
            JOIN users u ON ak.user_id = u.id
            WHERE ak.api_key = ? AND ak.is_active = TRUE
        """, (hashed_key,))
        
        row = cursor.fetchone()
        
        if not row:
            return None
        
        key_id, user_id, permissions, expires_at, email, name = row
        
        # Check expiration
        if expires_at:
            expires_dt = datetime.fromisoformat(expires_at)
            if datetime.now() > expires_dt:
                logger.warning(f"Expired API key used: {api_key[:12]}...")
                return None
        
        # Update last used and usage count
        cursor.execute("""
            UPDATE api_keys
            SET last_used_at = CURRENT_TIMESTAMP,
                usage_count = usage_count + 1
            WHERE id = ?
        """, (key_id,))
        conn.commit()
        
        return {
            "key_id": key_id,
            "user_id": user_id,
            "email": email,
            "name": name,
            "permissions": permissions.split(",")
        }


def revoke_api_key(key_id: str, user_id: str) -> bool:
    """
    Revoke (deactivate) an API key
    
    Args:
        key_id: API key ID
        user_id: User ID (for authorization)
        
    Returns:
        bool: True if revoked successfully
    """
    with get_connection() as (conn, cursor):
        cursor.execute("""
            UPDATE api_keys
            SET is_active = FALSE
            WHERE id = ? AND user_id = ?
        """, (key_id, user_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"API key revoked: {key_id}")
            return True
        
        return False


def delete_api_key(key_id: str, user_id: str) -> bool:
    """
    Permanently delete an API key
    
    Args:
        key_id: API key ID
        user_id: User ID (for authorization)
        
    Returns:
        bool: True if deleted successfully
    """
    with get_connection() as (conn, cursor):
        cursor.execute("""
            DELETE FROM api_keys
            WHERE id = ? AND user_id = ?
        """, (key_id, user_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"API key deleted: {key_id}")
            return True
        
        return False


def log_api_key_usage(
    key_id: str,
    endpoint: str,
    method: str,
    status_code: int,
    ip_address: str,
    user_agent: str
):
    """Log API key usage for analytics"""
    import uuid
    
    with get_connection() as (conn, cursor):
        cursor.execute("""
            INSERT INTO api_key_usage (
                id, api_key_id, endpoint, method, status_code,
                ip_address, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), key_id, endpoint, method,
            status_code, ip_address, user_agent
        ))
        conn.commit()


def get_api_key_usage_stats(key_id: str, days: int = 30) -> Dict[str, Any]:
    """Get usage statistics for an API key"""
    from datetime import datetime, timedelta
    
    since_date = datetime.now() - timedelta(days=days)
    
    with get_connection() as (conn, cursor):
        # Total calls
        cursor.execute("""
            SELECT COUNT(*) FROM api_key_usage
            WHERE api_key_id = ? AND created_at >= ?
        """, (key_id, since_date))
        total_calls = cursor.fetchone()[0]
        
        # Calls by endpoint
        cursor.execute("""
            SELECT endpoint, COUNT(*) as count
            FROM api_key_usage
            WHERE api_key_id = ? AND created_at >= ?
            GROUP BY endpoint
            ORDER BY count DESC
            LIMIT 10
        """, (key_id, since_date))
        
        by_endpoint = [
            {"endpoint": row[0], "count": row[1]}
            for row in cursor.fetchall()
        ]
        
        # Calls by day
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM api_key_usage
            WHERE api_key_id = ? AND created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """, (key_id, since_date))
        
        by_day = [
            {"date": row[0], "count": row[1]}
            for row in cursor.fetchall()
        ]
        
        return {
            "total_calls": total_calls,
            "by_endpoint": by_endpoint,
            "by_day": by_day,
            "period_days": days
        }
