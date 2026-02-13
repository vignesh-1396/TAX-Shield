from app.db.session import get_connection, row_to_dict
from app.db.crud import batch as batch_crud

def check_state():
    print("Checking Batch Jobs...")
    with get_connection() as (conn, cursor):
        cursor.execute("SELECT * FROM batch_jobs ORDER BY created_at DESC LIMIT 5")
        jobs = [row_to_dict(row) for row in cursor.fetchall()]
        
        for job in jobs:
            print(f"\nJob ID: {job['id']}")
            print(f"Status: {job['status']}")
            print(f"Created: {job['created_at']}")
            print(f"Counts: Total={job['total_count']}, Processed={job['processed_count']}")
            print(f"Output: {job['output_filename']}")
            
            # Check items
            cursor.execute("SELECT status, count(*) as cnt FROM batch_items WHERE batch_id = %s GROUP BY status", (job['id'],))
            item_stats = cursor.fetchall()
            print("Item Statuses:", [dict(row) for row in item_stats])

if __name__ == "__main__":
    check_state()
