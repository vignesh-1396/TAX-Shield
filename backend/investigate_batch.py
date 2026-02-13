import os
import sys

# Add current directory to python path
sys.path.append(os.getcwd())

from app.db.session import get_connection

def investigate():
    print("Investigating 'itc_gaurd.batch_jobs'...")
    with get_connection() as (conn, cursor):
        # Check 'batch_jobs' table columns in itc_gaurd
        print("\nColumns in 'itc_gaurd.batch_jobs':")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'batch_jobs'
            AND table_schema = 'itc_gaurd'
        """)
        cols = cursor.fetchall()
        for row in cols:
            print(f" - {row['column_name']} ({row['data_type']})")

if __name__ == "__main__":
    investigate()
