import os
import sys

# Add current directory to python path
sys.path.append(os.getcwd())

from app.db.session import get_connection

def investigate():
    print("Investigating Database Schema...")
    with get_connection() as (conn, cursor):
        # 1. Check Current Search Path
        cursor.execute("SHOW search_path")
        print(f"Current Search Path: {cursor.fetchone()}")

        # 2. List all tables in itc_gaurd schema
        print("\nTables in 'itc_gaurd' schema:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'itc_gaurd'
        """)
        for row in cursor.fetchall():
            print(f" - {row['table_name']}")

        # 3. Check 'users' table columns
        print("\nColumns in 'users' table:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        cols = cursor.fetchall()
        if not cols:
            print("No 'users' table found in current search path or it's empty.")
        else:
            for row in cols:
                print(f" - {row['column_name']} ({row['data_type']})")

if __name__ == "__main__":
    investigate()
