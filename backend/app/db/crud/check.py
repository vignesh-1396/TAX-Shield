from typing import Optional, List, Dict
from app.db.session import get_connection, ph, row_to_dict, DB_ENGINE

def save_compliance_check(
    gstin: str,
    vendor_name: str,
    amount: float,
    decision: str,
    rule_id: str,
    reason: str,
    risk_level: str,
    data_source: str,
    certificate_url: str = None
) -> int:
    """Save compliance check result and return ID"""
    with get_connection() as (conn, cursor):
        if DB_ENGINE == "postgres":
            cursor.execute(f"""
                INSERT INTO compliance_checks 
                (gstin, vendor_name, amount, decision, rule_id, reason, risk_level, data_source, certificate_url)
                VALUES ({ph(9)})
                RETURNING id
            """, (gstin, vendor_name, amount, decision, rule_id, reason, risk_level, data_source, certificate_url))
            check_id = cursor.fetchone()["id"]
        else:
            cursor.execute(f"""
                INSERT INTO compliance_checks 
                (gstin, vendor_name, amount, decision, rule_id, reason, risk_level, data_source, certificate_url)
                VALUES ({ph(9)})
            """, (gstin, vendor_name, amount, decision, rule_id, reason, risk_level, data_source, certificate_url))
            check_id = cursor.lastrowid
        
        conn.commit()
    
    return check_id


def get_recent_checks(limit: int = 50) -> List[Dict]:
    """Get recent compliance checks"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            SELECT * FROM compliance_checks 
            ORDER BY created_at DESC 
            LIMIT {ph()}
        """, (limit,))
        
        rows = cursor.fetchall()
    
    return [row_to_dict(row) for row in rows]


def get_check_by_id(check_id: int) -> Optional[Dict]:
    """Get a specific compliance check by ID"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            SELECT * FROM compliance_checks 
            WHERE id = {ph()}
        """, (check_id,))
        
        row = cursor.fetchone()
    
    return row_to_dict(row)


def get_checks_by_gstin(gstin: str) -> List[Dict]:
    """Get all checks for a specific GSTIN"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            SELECT * FROM compliance_checks 
            WHERE gstin = {ph()}
            ORDER BY created_at DESC
        """, (gstin,))
        
        rows = cursor.fetchall()
    
    return [row_to_dict(row) for row in rows]
