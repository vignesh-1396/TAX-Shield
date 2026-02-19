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


# ===== REPORTS FUNCTIONS =====

def get_checks_summary(start_date: str = None, end_date: str = None) -> Dict:
    """Get compliance check summary statistics for a date range"""
    with get_connection() as (conn, cursor):
        # Build date filter
        date_filter = ""
        params = []
        
        if start_date and end_date:
            date_filter = f"WHERE DATE(created_at) BETWEEN {ph()} AND {ph()}"
            params = [start_date, end_date]
        elif start_date:
            date_filter = f"WHERE DATE(created_at) >= {ph()}"
            params = [start_date]
        elif end_date:
            date_filter = f"WHERE DATE(created_at) <= {ph()}"
            params = [end_date]
        
        # Total checks
        cursor.execute(f"SELECT COUNT(*) as total FROM compliance_checks {date_filter}", params)
        total = cursor.fetchone()[0]
        
        # Decision breakdown
        cursor.execute(f"""
            SELECT decision, COUNT(*) as count 
            FROM compliance_checks {date_filter}
            GROUP BY decision
        """, params)
        decisions = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Risk level breakdown
        cursor.execute(f"""
            SELECT risk_level, COUNT(*) as count 
            FROM compliance_checks {date_filter}
            GROUP BY risk_level
        """, params)
        risk_levels = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Amount statistics
        cursor.execute(f"""
            SELECT 
                SUM(amount) as total_amount,
                SUM(CASE WHEN decision = 'RELEASE' THEN amount ELSE 0 END) as released_amount,
                SUM(CASE WHEN decision IN ('HOLD', 'STOP') THEN amount ELSE 0 END) as blocked_amount
            FROM compliance_checks {date_filter}
        """, params)
        amounts = cursor.fetchone()
        
        return {
            "total_checks": total,
            "decisions": {
                "RELEASE": decisions.get("RELEASE", 0),
                "HOLD": decisions.get("HOLD", 0),
                "STOP": decisions.get("STOP", 0)
            },
            "risk_levels": {
                "LOW": risk_levels.get("LOW", 0),
                "MEDIUM": risk_levels.get("MEDIUM", 0),
                "HIGH": risk_levels.get("HIGH", 0),
                "CRITICAL": risk_levels.get("CRITICAL", 0)
            },
            "amounts": {
                "total": amounts[0] or 0,
                "released": amounts[1] or 0,
                "blocked": amounts[2] or 0
            },
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }


def get_high_risk_checks(start_date: str = None, end_date: str = None) -> List[Dict]:
    """Get all HOLD and STOP checks for a date range"""
    with get_connection() as (conn, cursor):
        # Build query
        query = f"""
            SELECT * FROM compliance_checks 
            WHERE decision IN ({ph()}, {ph()})
        """
        params = ['HOLD', 'STOP']
        
        if start_date and end_date:
            query += f" AND DATE(created_at) BETWEEN {ph()} AND {ph()}"
            params.extend([start_date, end_date])
        elif start_date:
            query += f" AND DATE(created_at) >= {ph()}"
            params.append(start_date)
        elif end_date:
            query += f" AND DATE(created_at) <= {ph()}"
            params.append(end_date)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
    
    return [row_to_dict(row) for row in rows]


def get_checks_by_date_range(start_date: str = None, end_date: str = None, limit: int = 1000) -> List[Dict]:
    """Get all compliance checks for a date range (for audit trail)"""
    with get_connection() as (conn, cursor):
        query = "SELECT * FROM compliance_checks"
        params = []
        
        if start_date and end_date:
            query += f" WHERE DATE(created_at) BETWEEN {ph()} AND {ph()}"
            params = [start_date, end_date]
        elif start_date:
            query += f" WHERE DATE(created_at) >= {ph()}"
            params = [start_date]
        elif end_date:
            query += f" WHERE DATE(created_at) <= {ph()}"
            params = [end_date]
        
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
    
    return [row_to_dict(row) for row in rows]
