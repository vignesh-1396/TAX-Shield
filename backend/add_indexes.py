"""
Add indexes to gstr_2b_data table using raw SQL execution.
"""
import sys
sys.path.insert(0, '/Volumes/Vicky\'s SD /Startup IDea/ITC_Protection_System/backend')

from app.db.session import get_connection
import psycopg2

def add_indexes():
    """Add indexes to gstr_2b_data table for faster queries."""
    
    print("Adding database indexes...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Index on (user_id, return_period) for fast filtering
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_gstr2b_user_period 
                    ON itc_gaurd.gstr_2b_data(user_id, return_period);
                """)
                print("✅ Created index: idx_gstr2b_user_period")
                
                # Index on gstin for join operations
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_gstr2b_gstin 
                    ON itc_gaurd.gstr_2b_data(gstin);
                """)
                print("✅ Created index: idx_gstr2b_gstin")
                
                # Composite index for common query pattern
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_gstr2b_lookup 
                    ON itc_gaurd.gstr_2b_data(user_id, return_period, gstin);
                """)
                print("✅ Created index: idx_gstr2b_lookup")
                
                conn.commit()
                print("\n✅ All indexes created successfully!")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_indexes()
