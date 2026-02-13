"""
ITC Shield - Database Layer
Supports both SQLite (local development) and PostgreSQL (production).

Usage:
  - No DATABASE_URL env var → SQLite (itc_shield.db)
  - DATABASE_URL set → PostgreSQL
"""
import os
import json
from datetime import datetime
from typing import Optional, List, Dict
from contextlib import contextmanager

# ============ DATABASE ENGINE DETECTION ============

DATABASE_URL = os.getenv("DATABASE_URL")
DB_ENGINE = "postgres" if DATABASE_URL else "sqlite"

# Connection pool (PostgreSQL only)
_pg_pool = None


def _init_pg_pool():
    """Initialize PostgreSQL connection pool"""
    global _pg_pool
    if _pg_pool is None:
        import psycopg2
        import psycopg2.pool
        _pg_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL
        )
    return _pg_pool


# ============ CONNECTION HELPER ============

@contextmanager
def get_connection():
    """
    Get a database connection as a context manager.
    
    Usage:
        with get_connection() as (conn, cursor):
            cursor.execute(...)
            conn.commit()
    """
    if DB_ENGINE == "postgres":
        import psycopg2
        import psycopg2.extras
        pool = _init_pg_pool()
        conn = pool.getconn()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            yield conn, cursor
        finally:
            cursor.close()
            pool.putconn(conn)
    else:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "itc_shield.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            yield conn, cursor
        finally:
            conn.close()


def _ph(count=1):
    """Return placeholder(s) for the current engine: %s for PG, ? for SQLite"""
    placeholder = "%s" if DB_ENGINE == "postgres" else "?"
    if count == 1:
        return placeholder
    return ", ".join([placeholder] * count)


def _row_to_dict(row):
    """Convert a row to a dict regardless of engine"""
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    return dict(row)


# ============ INITIALIZATION ============

def init_database():
    """Initialize database tables"""
    if DB_ENGINE == "postgres":
        _init_postgres_tables()
    else:
        _init_sqlite_tables()
    print(f"Database initialized (engine: {DB_ENGINE})")


def _init_postgres_tables():
    """Create tables using PostgreSQL syntax"""
    with get_connection() as (conn, cursor):
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                company_name TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                last_login TIMESTAMP
            )
        """)
        
        # Vendors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                gstin TEXT PRIMARY KEY,
                legal_name TEXT,
                trade_name TEXT,
                gst_status TEXT,
                registration_date TEXT,
                last_synced_at TIMESTAMP,
                raw_data TEXT
            )
        """)
        
        # Compliance checks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_checks (
                id SERIAL PRIMARY KEY,
                gstin TEXT NOT NULL,
                vendor_name TEXT,
                amount REAL,
                decision TEXT NOT NULL,
                rule_id TEXT,
                reason TEXT,
                risk_level TEXT,
                data_source TEXT,
                certificate_url TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                created_by TEXT
            )
        """)
        
        # Overrides table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS overrides (
                id SERIAL PRIMARY KEY,
                check_id INTEGER REFERENCES compliance_checks(id),
                original_decision TEXT,
                new_decision TEXT,
                reason TEXT,
                approved_by TEXT,
                approved_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Batch jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_jobs (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                status TEXT DEFAULT 'PENDING',
                total_count INTEGER DEFAULT 0,
                processed_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                input_filename TEXT,
                output_filename TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP,
                error_message TEXT
            )
        """)
        
        # Batch items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_items (
                id SERIAL PRIMARY KEY,
                batch_id TEXT NOT NULL REFERENCES batch_jobs(id),
                gstin TEXT NOT NULL,
                vendor_name TEXT,
                amount REAL,
                decision TEXT,
                check_id INTEGER REFERENCES compliance_checks(id),
                status TEXT DEFAULT 'PENDING',
                error_message TEXT
            )
        """)
        
        conn.commit()


def _init_sqlite_tables():
    """Create tables using SQLite syntax"""
    with get_connection() as (conn, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                company_name TEXT,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                last_login TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                gstin TEXT PRIMARY KEY,
                legal_name TEXT,
                trade_name TEXT,
                gst_status TEXT,
                registration_date TEXT,
                last_synced_at TEXT,
                raw_data TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gstin TEXT NOT NULL,
                vendor_name TEXT,
                amount REAL,
                decision TEXT NOT NULL,
                rule_id TEXT,
                reason TEXT,
                risk_level TEXT,
                data_source TEXT,
                certificate_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS overrides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_id INTEGER,
                original_decision TEXT,
                new_decision TEXT,
                reason TEXT,
                approved_by TEXT,
                approved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (check_id) REFERENCES compliance_checks(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_jobs (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                status TEXT DEFAULT 'PENDING',
                total_count INTEGER DEFAULT 0,
                processed_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                input_filename TEXT,
                output_filename TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                error_message TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                gstin TEXT NOT NULL,
                vendor_name TEXT,
                amount REAL,
                decision TEXT,
                check_id INTEGER,
                status TEXT DEFAULT 'PENDING',
                error_message TEXT,
                FOREIGN KEY (batch_id) REFERENCES batch_jobs(id),
                FOREIGN KEY (check_id) REFERENCES compliance_checks(id)
            )
        """)
        
        conn.commit()


# ============ VENDOR FUNCTIONS ============

def save_vendor(vendor_data: Dict):
    """Save or update vendor data"""
    ph = _ph
    with get_connection() as (conn, cursor):
        if DB_ENGINE == "postgres":
            cursor.execute(f"""
                INSERT INTO vendors 
                (gstin, legal_name, trade_name, gst_status, registration_date, last_synced_at, raw_data)
                VALUES ({_ph(7)})
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
                VALUES ({_ph(7)})
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
            SELECT * FROM vendors WHERE gstin = {_ph()}
        """, (gstin,))
        
        row = cursor.fetchone()
    
    if row:
        row = _row_to_dict(row)
        last_synced = datetime.fromisoformat(str(row["last_synced_at"]))
        age_hours = (datetime.now() - last_synced).total_seconds() / 3600
        
        if age_hours <= max_age_hours:
            return json.loads(row["raw_data"])
    
    return None


# ============ COMPLIANCE CHECK FUNCTIONS ============

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
                VALUES ({_ph(9)})
                RETURNING id
            """, (gstin, vendor_name, amount, decision, rule_id, reason, risk_level, data_source, certificate_url))
            check_id = cursor.fetchone()["id"]
        else:
            cursor.execute(f"""
                INSERT INTO compliance_checks 
                (gstin, vendor_name, amount, decision, rule_id, reason, risk_level, data_source, certificate_url)
                VALUES ({_ph(9)})
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
            LIMIT {_ph()}
        """, (limit,))
        
        rows = cursor.fetchall()
    
    return [_row_to_dict(row) for row in rows]


def get_check_by_id(check_id: int) -> Optional[Dict]:
    """Get a specific compliance check by ID"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            SELECT * FROM compliance_checks 
            WHERE id = {_ph()}
        """, (check_id,))
        
        row = cursor.fetchone()
    
    return _row_to_dict(row)


def get_checks_by_gstin(gstin: str) -> List[Dict]:
    """Get all checks for a specific GSTIN"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            SELECT * FROM compliance_checks 
            WHERE gstin = {_ph()}
            ORDER BY created_at DESC
        """, (gstin,))
        
        rows = cursor.fetchall()
    
    return [_row_to_dict(row) for row in rows]


# ============ BATCH JOB FUNCTIONS ============

def create_batch_job(job_id: str, total_count: int, input_filename: str) -> str:
    """Create a new batch job"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            INSERT INTO batch_jobs (id, total_count, input_filename, status)
            VALUES ({_ph(4)})
        """, (job_id, total_count, input_filename, 'PENDING'))
        
        conn.commit()
    return job_id


def add_batch_items(batch_id: str, items: List[Dict]):
    """Add multiple items to a batch job"""
    with get_connection() as (conn, cursor):
        for item in items:
            cursor.execute(f"""
                INSERT INTO batch_items (batch_id, gstin, vendor_name, amount, status)
                VALUES ({_ph(5)})
            """, (batch_id, item['gstin'], item.get('vendor_name', ''), item.get('amount', 0), 'PENDING'))
        
        conn.commit()


def get_batch_job(job_id: str) -> Optional[Dict]:
    """Get batch job by ID"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"SELECT * FROM batch_jobs WHERE id = {_ph()}", (job_id,))
        row = cursor.fetchone()
    
    return _row_to_dict(row)


def get_batch_items(batch_id: str, status: str = None) -> List[Dict]:
    """Get items in a batch job, optionally filtered by status"""
    with get_connection() as (conn, cursor):
        if status:
            cursor.execute(f"""
                SELECT * FROM batch_items WHERE batch_id = {_ph()} AND status = {_ph()}
            """, (batch_id, status))
        else:
            cursor.execute(f"SELECT * FROM batch_items WHERE batch_id = {_ph()}", (batch_id,))
        
        rows = cursor.fetchall()
    
    return [_row_to_dict(row) for row in rows]


def update_batch_job_status(job_id: str, status: str, error_message: str = None):
    """Update batch job status"""
    with get_connection() as (conn, cursor):
        if status in ('COMPLETED', 'FAILED'):
            cursor.execute(f"""
                UPDATE batch_jobs 
                SET status = {_ph()}, completed_at = {_ph()}, error_message = {_ph()}
                WHERE id = {_ph()}
            """, (status, datetime.now().isoformat(), error_message, job_id))
        else:
            cursor.execute(f"""
                UPDATE batch_jobs SET status = {_ph()} WHERE id = {_ph()}
            """, (status, job_id))
        
        conn.commit()


def update_batch_job_progress(job_id: str, processed: int, success: int, failed: int):
    """Update batch job progress counters"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            UPDATE batch_jobs 
            SET processed_count = {_ph()}, success_count = {_ph()}, failed_count = {_ph()}
            WHERE id = {_ph()}
        """, (processed, success, failed, job_id))
        
        conn.commit()


def update_batch_item(item_id: int, status: str, decision: str = None, 
                      check_id: int = None, error_message: str = None):
    """Update a batch item after processing"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            UPDATE batch_items 
            SET status = {_ph()}, decision = {_ph()}, check_id = {_ph()}, error_message = {_ph()}
            WHERE id = {_ph()}
        """, (status, decision, check_id, error_message, item_id))
        
        conn.commit()


def set_batch_output_file(job_id: str, output_filename: str):
    """Set the output ZIP filename for a batch job"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            UPDATE batch_jobs SET output_filename = {_ph()} WHERE id = {_ph()}
        """, (output_filename, job_id))
        
        conn.commit()


# Initialize database on import
init_database()
