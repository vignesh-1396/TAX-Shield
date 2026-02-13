import os
import sys

# Add current directory to python path
sys.path.append(os.getcwd())

from app.db.crud import gstr2b_data
from app.db.session import get_connection

def debug_crud():
    user_email = "vigneshiba132696@gmail.com"
    period = "112024"
    
    print(f"Debugging CRUD for user {user_email}, period {period}")
    
    with get_connection() as (conn, cursor):
        cursor.execute("SELECT id FROM users WHERE email=%s", (user_email,))
        user = cursor.fetchone()
        if not user:
            print("User not found!")
            return
        user_id = user['id']
        print(f"Found User ID: {user_id} (Type: {type(user_id)})")

    invoices = gstr2b_data.get_invoices_by_period(user_id, period)
    print(f"Result count: {len(invoices)}")
    if len(invoices) > 0:
        print("First invoice:", invoices[0])
    else:
        # Check what's in the table for any user
        with get_connection() as (conn, cursor):
            cursor.execute("SELECT user_id, return_period FROM gstr_2b_data LIMIT 5")
            rows = cursor.fetchall()
            print("Existing records in table (user_id, period):")
            for r in rows:
                print(f" - {r['user_id']} ({type(r['user_id'])}), {r['return_period']}")

if __name__ == "__main__":
    debug_crud()
