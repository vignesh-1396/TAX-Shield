"""
Run API Key Database Migrations
"""
import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run API key table migrations"""
    
    # Use SQLite database
    db_path = os.path.join(os.path.dirname(__file__), "itc_shield.db")
    
    # Create api_keys table
    CREATE_API_KEYS_TABLE = """
    CREATE TABLE IF NOT EXISTS api_keys (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        key_name TEXT NOT NULL,
        api_key TEXT UNIQUE NOT NULL,
        key_prefix TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_used_at TIMESTAMP,
        expires_at TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        permissions TEXT DEFAULT 'read,write',
        usage_count INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    
    # Create indexes
    CREATE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(api_key);",
        "CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);"
    ]
    
    # Create api_key_usage table
    CREATE_API_KEY_USAGE_TABLE = """
    CREATE TABLE IF NOT EXISTS api_key_usage (
        id TEXT PRIMARY KEY,
        api_key_id TEXT NOT NULL,
        endpoint TEXT NOT NULL,
        method TEXT NOT NULL,
        status_code INTEGER,
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (api_key_id) REFERENCES api_keys(id) ON DELETE CASCADE
    );
    """
    
    # Create usage indexes
    CREATE_USAGE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_api_key_usage_key_id ON api_key_usage(api_key_id);",
        "CREATE INDEX IF NOT EXISTS idx_api_key_usage_created_at ON api_key_usage(created_at);"
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        logger.info(f"Running API key migrations on {db_path}...")
        
        # Create tables
        cursor.execute(CREATE_API_KEYS_TABLE)
        logger.info("✓ Created api_keys table")
        
        cursor.execute(CREATE_API_KEY_USAGE_TABLE)
        logger.info("✓ Created api_key_usage table")
        
        # Create indexes
        for idx_sql in CREATE_INDEXES:
            cursor.execute(idx_sql)
        logger.info("✓ Created api_keys indexes")
        
        for idx_sql in CREATE_USAGE_INDEXES:
            cursor.execute(idx_sql)
        logger.info("✓ Created api_key_usage indexes")
        
        conn.commit()
        logger.info("✅ API key migrations completed successfully!")
        
    finally:
        conn.close()


if __name__ == "__main__":
    run_migrations()
