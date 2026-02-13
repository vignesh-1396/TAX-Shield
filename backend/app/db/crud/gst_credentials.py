"""
CRUD Operations for GST Credentials
Handles storing and retrieving GST authentication tokens
"""
import uuid
from datetime import datetime
from typing import Optional, Dict
from app.db.session import get_connection, ph
import logging

logger = logging.getLogger(__name__)


def create_gst_credential(
    user_id: str,
    gstin: str,
    username: str,
    auth_token: str,
    token_expiry: str
) -> Optional[str]:
    """
    Store GST credentials after successful OTP verification.
    
    Args:
        user_id: User ID
        gstin: GSTIN
        username: GST Portal username
        auth_token: Encrypted auth token
        token_expiry: Token expiration timestamp
        
    Returns:
        Credential ID if successful, None otherwise
    """
    try:
        credential_id = str(uuid.uuid4())
        
        with get_connection() as (conn, cursor):
            cursor.execute(f"""
                INSERT INTO gst_credentials (
                    id, user_id, gstin, username, auth_token,
                    token_expiry, is_active, created_at, updated_at
                ) VALUES ({ph(9)})
            """, (
                credential_id, user_id, gstin, username, auth_token,
                token_expiry, True, datetime.now().isoformat(), datetime.now().isoformat()
            ))
            conn.commit()
        
        logger.info(f"GST credential created for GSTIN: {gstin}")
        return credential_id
        
    except Exception as e:
        logger.error(f"Error creating GST credential: {str(e)}")
        return None


def get_gst_credential(user_id: str, gstin: str) -> Optional[Dict]:
    """
    Get active GST credential for a user's GSTIN.
    
    Args:
        user_id: User ID
        gstin: GSTIN
        
    Returns:
        Credential dict if found, None otherwise
    """
    try:
        with get_connection() as (conn, cursor):
            cursor.execute(f"""
                SELECT id, gstin, username, auth_token, token_expiry,
                       is_active, created_at, updated_at
                FROM gst_credentials
                WHERE user_id = {ph()} AND gstin = {ph()} AND is_active = {ph()}
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id, gstin, True))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "gstin": row[1],
                    "username": row[2],
                    "auth_token": row[3],
                    "token_expiry": row[4],
                    "is_active": bool(row[5]),
                    "created_at": row[6],
                    "updated_at": row[7]
                }
            return None
            
    except Exception as e:
        logger.error(f"Error fetching GST credential: {str(e)}")
        return None


def update_gst_credential(
    credential_id: str,
    auth_token: str,
    token_expiry: str
) -> bool:
    """
    Update GST credential with new token (after refresh).
    
    Args:
        credential_id: Credential ID
        auth_token: New auth token
        token_expiry: New expiry timestamp
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_connection() as (conn, cursor):
            cursor.execute(f"""
                UPDATE gst_credentials
                SET auth_token = {ph()},
                    token_expiry = {ph()},
                    updated_at = {ph()}
                WHERE id = {ph()}
            """, (auth_token, token_expiry, datetime.now().isoformat(), credential_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
    except Exception as e:
        logger.error(f"Error updating GST credential: {str(e)}")
        return False


def deactivate_gst_credential(user_id: str, gstin: str) -> bool:
    """
    Deactivate GST credential (disconnect GSTIN).
    
    Args:
        user_id: User ID
        gstin: GSTIN
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_connection() as (conn, cursor):
            cursor.execute(f"""
                UPDATE gst_credentials
                SET is_active = {ph()},
                    updated_at = {ph()}
                WHERE user_id = {ph()} AND gstin = {ph()}
            """, (False, datetime.now().isoformat(), user_id, gstin))
            
            conn.commit()
            return cursor.rowcount > 0
            
    except Exception as e:
        logger.error(f"Error deactivating GST credential: {str(e)}")
        return False


def get_user_gst_credentials(user_id: str) -> list:
    """
    Get all GST credentials for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        List of credential dicts
    """
    try:
        with get_connection() as (conn, cursor):
            cursor.execute(f"""
                SELECT id, gstin, username, token_expiry, is_active, created_at
                FROM gst_credentials
                WHERE user_id = {ph()}
                ORDER BY created_at DESC
            """, (user_id,))
            
            credentials = []
            for row in cursor.fetchall():
                credentials.append({
                    "id": row[0],
                    "gstin": row[1],
                    "username": row[2],
                    "token_expiry": row[3],
                    "is_active": bool(row[4]),
                    "created_at": row[5]
                })
            
            return credentials
            
    except Exception as e:
        logger.error(f"Error fetching user GST credentials: {str(e)}")
        return []
