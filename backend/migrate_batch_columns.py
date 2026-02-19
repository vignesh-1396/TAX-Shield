"""
Database migration to add risk_level and reason columns to batch_items table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in environment")
    exit(1)

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("Connected to database successfully")
    
    # Check current columns
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'batch_items'
        ORDER BY ordinal_position
    """)
    
    current_columns = [row[0] for row in cursor.fetchall()]
    print(f"Current batch_items columns: {current_columns}")
    
    # Add risk_level column if not exists
    if 'risk_level' not in current_columns:
        print("Adding risk_level column...")
        cursor.execute("""
            ALTER TABLE batch_items 
            ADD COLUMN risk_level VARCHAR(50)
        """)
        print("✓ risk_level column added")
    else:
        print("✓ risk_level column already exists")
    
    # Add reason column if not exists
    if 'reason' not in current_columns:
        print("Adding reason column...")
        cursor.execute("""
            ALTER TABLE batch_items 
            ADD COLUMN reason TEXT
        """)
        print("✓ reason column added")
    else:
        print("✓ reason column already exists")
    
    # Commit changes
    conn.commit()
    print("\n✅ Migration completed successfully!")
    
    # Verify changes
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'batch_items'
        ORDER BY ordinal_position
    """)
    
    updated_columns = [row[0] for row in cursor.fetchall()]
    print(f"\nUpdated batch_items columns: {updated_columns}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Migration failed: {str(e)}")
    exit(1)
