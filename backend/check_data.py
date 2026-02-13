import os
import sys

# Add current directory to python path
sys.path.append(os.getcwd())

from app.db.session import get_connection

def investigate():
    print("Checking 'gstr_2b_data' Content...")
    user_id = '20697d61-5e46-4a63-8a2b-8bfa8fb74cf4'
    period = '112024'
    
    with get_connection() as (conn, cursor):
        # 1. Check Total Count
        cursor.execute("SELECT COUNT(*) FROM gstr_2b_data")
        total = list(cursor.fetchone().values())[0]
        print(f"Total records in table: {total}")
        
        # 2. Check for specific user and period
        cursor.execute("""
            SELECT COUNT(*) FROM gstr_2b_data 
            WHERE user_id = %s AND return_period = %s
        """, (user_id, period))
        match_count = list(cursor.fetchone().values())[0]
        print(f"Records for user {user_id} and period {period}: {match_count}")
        
        # 3. List some records
        if match_count > 0:
            cursor.execute("SELECT * FROM gstr_2b_data LIMIT 5")
            for row in cursor.fetchall():
                print(f" - {row}")

if __name__ == "__main__":
    investigate()
