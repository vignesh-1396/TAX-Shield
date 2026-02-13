import os
import sys

# Add current directory to python path
sys.path.append(os.getcwd())

from app.db.session import get_connection

def cleanup():
    print("Cleaning up redundant tables in 'public' schema...")
    tables_to_drop = [
        "gstr_2b_data",
        "gst_credentials",
        "batch_items",
        "batch_jobs",
        "overrides",
        "compliance_checks"
    ]
    
    with get_connection() as (conn, cursor):
        # We need to set search_path to public specifically for this cleanup
        cursor.execute("SET search_path TO public")
        
        for table in tables_to_drop:
            try:
                print(f"Dropping table 'public.{table}'...")
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            except Exception as e:
                print(f"Error dropping {table}: {e}")
        
        conn.commit()
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup()
