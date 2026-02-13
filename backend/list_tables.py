import os
import sys

# Add current directory to python path
sys.path.append(os.getcwd())

from app.db.session import get_connection

def investigate():
    print("Listing All Tables...")
    with get_connection() as (conn, cursor):
        # List tables in itc_gaurd
        print("\nTables in 'itc_gaurd':")
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'itc_gaurd'")
        for row in cursor.fetchall():
            print(f" - {row['table_name']}")
            
        # List tables in public
        print("\nTables in 'public':")
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        for row in cursor.fetchall():
            print(f" - {row['table_name']}")

if __name__ == "__main__":
    investigate()
