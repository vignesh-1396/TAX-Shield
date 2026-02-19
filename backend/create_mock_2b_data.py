import os
import sys
import uuid
from datetime import datetime

# Add current directory to python path
sys.path.append(os.getcwd())

from app.db.session import get_connection, ph, init_database

def create_mock_data():
    # Initialize tables in itc_gaurd schema
    init_database()
    
    print("Creating mock GSTR-2B data...")
    
    # User ID: Need to pick a valid user ID or insert a dummy one?
    # For now, let's assume we use the first available user or create one.
    # Actually, verify_otp endpoint uses current_user["id"].
    # I need to know the user_id that will be used for testing.
    # If I login as 'admin', I use that ID.
    
    # Let's just insert for a specific dummy user ID and use that in testing?
    # Or query existing users.
    
    user_id = None
    with get_connection() as (conn, cursor):
        cursor.execute("SELECT id, email FROM users LIMIT 1")
        row = cursor.fetchone()
        if row:
            user_id = row['id']
            print(f"Using existing user: {row['email']} ({user_id})")
        else:
            print("No users found. Creating dummy user...")
            user_id = str(uuid.uuid4())
            cursor.execute(f"INSERT INTO users (id, email, password_hash, is_active) VALUES ({ph(4)})", 
                           (user_id, "test@example.com", "dummy", True))
            conn.commit()

    if not user_id:
        print("Failed to get user ID")
        return

    # Delete existing data for return period 112024
    from app.db.crud.gstr2b_data import delete_gstr2b_data, bulk_insert_gstr2b_invoices
    delete_gstr2b_data(user_id, "112024")

    # Mock Data
    invoices = [
        {
            "supplier_gstin": "33AABCU9603R1ZX", # Matched
            "invoice_no": "INV-001",
            "invoice_date": "2024-11-01",
            "invoice_value": 11800.0,
            "taxable_value": 10000.0,
            "tax_amount": 1800.0,
            "filing_status": "Y",
            "return_period": "112024"
        },
        {
            "supplier_gstin": "27AADCB2230M1Z5", # Mismatch Amount
            "invoice_no": "INV-002",
            "invoice_date": "2024-11-05", 
            "invoice_value": 5900.0,
            "taxable_value": 5000.0,
            "tax_amount": 900.0, # PR has 1000
            "filing_status": "Y",
            "return_period": "112024"
        },
        {
            # Missing in PR (User forgot to record)
            "supplier_gstin": "29AABCT1234F1ZP",
            "invoice_no": "INV-003",
            "invoice_date": "2024-11-10",
            "invoice_value": 2360.0,
            "taxable_value": 2000.0,
            "tax_amount": 360.0,
            "filing_status": "Y",
            "return_period": "112024"
        }
    ]
    
    bulk_insert_gstr2b_invoices(user_id, invoices)
    print("Mock GSTR-2B data inserted successfully!")

if __name__ == "__main__":
    create_mock_data()
