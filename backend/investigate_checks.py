import os
import sys

# Add current directory to python path
sys.path.append(os.getcwd())

from app.db.session import get_connection

def investigate():
    print("Investigating 'compliance_checks' table...")
    with get_connection() as (conn, cursor):
        # Check 'compliance_checks' table columns
        print("\nColumns in 'compliance_checks' table:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'compliance_checks'
            AND table_schema = 'itc_gaurd'
        """)
        cols = cursor.fetchall()
        for row in cols:
            print(f" - {row['column_name']} ({row['data_type']})")

if __name__ == "__main__":
    investigate()
