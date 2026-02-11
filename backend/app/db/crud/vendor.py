import json
from datetime import datetime
from typing import Optional, Dict
from app.db.session import get_connection, ph, row_to_dict, DB_ENGINE

def save_vendor(vendor_data: Dict):
    """Save or update vendor data"""
    with get_connection() as (conn, cursor):
        if DB_ENGINE == "postgres":
            cursor.execute(f"""
                INSERT INTO vendors 
                (gstin, legal_name, trade_name, gst_status, registration_date, last_synced_at, raw_data)
                VALUES ({ph(7)})
                ON CONFLICT (gstin) DO UPDATE SET
                    legal_name = EXCLUDED.legal_name,
                    trade_name = EXCLUDED.trade_name,
                    gst_status = EXCLUDED.gst_status,
                    registration_date = EXCLUDED.registration_date,
                    last_synced_at = EXCLUDED.last_synced_at,
                    raw_data = EXCLUDED.raw_data
            """, (
                vendor_data.get("gstin"),
                vendor_data.get("legal_name"),
                vendor_data.get("trade_name"),
                vendor_data.get("gst_status"),
                vendor_data.get("registration_date"),
                datetime.now().isoformat(),
                json.dumps(vendor_data)
            ))
        else:
            cursor.execute(f"""
                INSERT OR REPLACE INTO vendors 
                (gstin, legal_name, trade_name, gst_status, registration_date, last_synced_at, raw_data)
                VALUES ({ph(7)})
            """, (
                vendor_data.get("gstin"),
                vendor_data.get("legal_name"),
                vendor_data.get("trade_name"),
                vendor_data.get("gst_status"),
                vendor_data.get("registration_date"),
                datetime.now().isoformat(),
                json.dumps(vendor_data)
            ))
        
        conn.commit()


def get_cached_vendor(gstin: str, max_age_hours: int = 24) -> Optional[Dict]:
    """Get cached vendor data if fresh enough"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            SELECT * FROM vendors WHERE gstin = {ph()}
        """, (gstin,))
        
        row = cursor.fetchone()
    
    if row:
        row = row_to_dict(row)
        last_synced = datetime.fromisoformat(str(row["last_synced_at"]))
        age_hours = (datetime.now() - last_synced).total_seconds() / 3600
        
        if age_hours <= max_age_hours:
            return json.loads(row["raw_data"])
    
    return None
