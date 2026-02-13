"""
Run GSTR-2B Implementation Database Migrations
Creating tables: gst_credentials, gstr_2b_data, otp_logs
"""
import logging
import sys
import os

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run GSTR-2B implementation migrations"""
    
    logger.info("Starting GSTR-2B database migrations...")
    
    with get_connection() as (conn, cursor):
        # Determine DB type
        if hasattr(conn, "dsn"): # Postgres (psycopg2)
            db_type = "postgres"
            logger.info("Detected Database: PostgreSQL")
        else:
            db_type = "sqlite"
            logger.info("Detected Database: SQLite")
            
        # SQL Definitions
        if db_type == "postgres":
            primary_key_uuid = "UUID PRIMARY KEY"
            fk_users = "TEXT REFERENCES users(id)" # Users ID is TEXT (UUID String)
            timestamp_now = "TIMESTAMP DEFAULT NOW()"
            boolean_type = "BOOLEAN"
            boolean_true = "TRUE" # Use TRUE for Postgres
            text_type = "TEXT"
            decimal_type = "DECIMAL(18, 2)"
            date_type = "DATE"
        else: # SQLite
            primary_key_uuid = "TEXT PRIMARY KEY"
            fk_users = "TEXT REFERENCES users(id)"
            timestamp_now = "TEXT DEFAULT CURRENT_TIMESTAMP"
            boolean_type = "INTEGER"  # SQLite bool is 0/1
            boolean_true = "1" # Use 1 for SQLite
            text_type = "TEXT"
            decimal_type = "REAL"
            date_type = "TEXT"

        # 1. GST Credentials Table
        CREATE_GST_CREDENTIALS = f"""
        CREATE TABLE IF NOT EXISTS gst_credentials (
            id {primary_key_uuid},
            user_id {fk_users},
            gstin {text_type} UNIQUE NOT NULL,
            username {text_type},
            auth_token {text_type}, -- Encrypted (future)
            token_expiry {timestamp_now},
            is_active {boolean_type} DEFAULT {boolean_true},
            created_at {timestamp_now},
            updated_at {timestamp_now}
        );
        """
        
        # 2. GSTR-2B Data Table
        CREATE_GSTR_2B_DATA = f"""
        CREATE TABLE IF NOT EXISTS gstr_2b_data (
            id {primary_key_uuid},
            user_id {fk_users},
            gstin_supplier {text_type},
            invoice_no {text_type},
            invoice_date {date_type},
            invoice_value {decimal_type},
            taxable_value {decimal_type},
            tax_amount {decimal_type},
            filing_status {text_type}, -- 'Y' or 'N'
            return_period {text_type}, -- e.g. '022026'
            source {text_type} DEFAULT 'GSTR-2B',
            created_at {timestamp_now}
        );
        """
        
        # 3. OTP Logs (Audit Trail)
        CREATE_OTP_LOGS = f"""
        CREATE TABLE IF NOT EXISTS otp_logs (
            id {primary_key_uuid},
            user_id {fk_users},
            gstin {text_type},
            transaction_id {text_type},
            request_type {text_type}, -- 'CONNECT', 'REFRESH'
            status {text_type}, -- 'PENDING', 'SUCCESS', 'FAILED'
            ip_address {text_type},
            created_at {timestamp_now}
        );
        """

        # Execute
        try:
            logger.info("Creating 'gst_credentials' table...")
            cursor.execute(CREATE_GST_CREDENTIALS)
            
            logger.info("Creating 'gstr_2b_data' table...")
            cursor.execute(CREATE_GSTR_2B_DATA)
            
            logger.info("Creating 'otp_logs' table...")
            cursor.execute(CREATE_OTP_LOGS)
            
            # Indexes
            logger.info("Creating indexes...")
            if db_type == "postgres":
                 cursor.execute("CREATE INDEX IF NOT EXISTS idx_gstr2b_reconcile ON gstr_2b_data(gstin_supplier, invoice_no, invoice_date);")
                 cursor.execute("CREATE INDEX IF NOT EXISTS idx_gstr2b_user ON gstr_2b_data(user_id);")
            else:
                 cursor.execute("CREATE INDEX IF NOT EXISTS idx_gstr2b_reconcile ON gstr_2b_data(gstin_supplier, invoice_no, invoice_date);")
                 cursor.execute("CREATE INDEX IF NOT EXISTS idx_gstr2b_user ON gstr_2b_data(user_id);")

            conn.commit()
            logger.info("✅ GSTR-2B Migrations Completed Successfully!")
            
        except Exception as e:
            logger.error(f"Migration Failed: {e}")
            if db_type == "sqlite":
                conn.rollback()
            else:
                conn.rollback()
            raise e

if __name__ == "__main__":
    run_migrations()
