import os
import json
from datetime import datetime
from typing import Optional, List, Dict
from contextlib import contextmanager
from app.core.config import settings

# ============ DATABASE ENGINE DETECTION ============

DATABASE_URL = settings.DATABASE_URL
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
        # In modular structure, we'll keep the DB in the root backend folder or app folder
        # For compatibility with existing data, we target the one in 'backend/'
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, "itc_shield.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            yield conn, cursor
        finally:
            conn.close()


def ph(count=1):
    """Return placeholder(s) for the current engine: %s for PG, ? for SQLite"""
    placeholder = "%s" if DB_ENGINE == "postgres" else "?"
    if count == 1:
        return placeholder
    return ", ".join([placeholder] * count)


def row_to_dict(row):
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
                error_message TEXT,
                risk_level TEXT,
                reason TEXT
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
                risk_level TEXT,
                reason TEXT,
                FOREIGN KEY (batch_id) REFERENCES batch_jobs(id),
                FOREIGN KEY (check_id) REFERENCES compliance_checks(id)
            )
        """)
        
        conn.commit()
