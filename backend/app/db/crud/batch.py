from typing import Optional, List, Dict
from datetime import datetime
from app.db.session import get_connection, ph, row_to_dict

def create_batch_job(job_id: str, total_count: int, input_filename: str) -> str:
    """Create a new batch job"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            INSERT INTO batch_jobs (id, total_count, input_filename, status)
            VALUES ({ph(4)})
        """, (job_id, total_count, input_filename, 'PENDING'))
        
        conn.commit()
    return job_id


def add_batch_items(batch_id: str, items: List[Dict]):
    """Add multiple items to a batch job"""
    with get_connection() as (conn, cursor):
        for item in items:
            cursor.execute(f"""
                INSERT INTO batch_items (batch_id, gstin, vendor_name, amount, status)
                VALUES ({ph(5)})
            """, (batch_id, item['gstin'], item.get('vendor_name', ''), item.get('amount', 0), 'PENDING'))
        
        conn.commit()


def get_batch_job(job_id: str) -> Optional[Dict]:
    """Get batch job by ID"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"SELECT * FROM batch_jobs WHERE id = {ph()}", (job_id,))
        row = cursor.fetchone()
    
    return row_to_dict(row)


def get_batch_items(batch_id: str, status: str = None) -> List[Dict]:
    """Get items in a batch job, optionally filtered by status"""
    with get_connection() as (conn, cursor):
        if status:
            cursor.execute(f"""
                SELECT * FROM batch_items WHERE batch_id = {ph()} AND status = {ph()}
            """, (batch_id, status))
        else:
            cursor.execute(f"SELECT * FROM batch_items WHERE batch_id = {ph()}", (batch_id,))
        
        rows = cursor.fetchall()
    
    return [row_to_dict(row) for row in rows]


def update_batch_job_status(job_id: str, status: str, error_message: str = None):
    """Update batch job status"""
    with get_connection() as (conn, cursor):
        if status in ('COMPLETED', 'FAILED'):
            cursor.execute(f"""
                UPDATE batch_jobs 
                SET status = {ph()}, completed_at = {ph()}, error_message = {ph()}
                WHERE id = {ph()}
            """, (status, datetime.now().isoformat(), error_message, job_id))
        else:
            cursor.execute(f"""
                UPDATE batch_jobs SET status = {ph()} WHERE id = {ph()}
            """, (status, job_id))
        
        conn.commit()


def update_batch_job_progress(job_id: str, processed: int, success: int, failed: int):
    """Update batch job progress counters"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            UPDATE batch_jobs 
            SET processed_count = {ph()}, success_count = {ph()}, failed_count = {ph()}
            WHERE id = {ph()}
        """, (processed, success, failed, job_id))
        
        conn.commit()


def update_batch_item(item_id: int, status: str, decision: str = None, 
                      check_id: int = None, error_message: str = None):
    """Update a batch item after processing"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            UPDATE batch_items 
            SET status = {ph()}, decision = {ph()}, check_id = {ph()}, error_message = {ph()}
            WHERE id = {ph()}
        """, (status, decision, check_id, error_message, item_id))
        
        conn.commit()


def set_batch_output_file(job_id: str, output_filename: str):
    """Set the output ZIP filename for a batch job"""
    with get_connection() as (conn, cursor):
        cursor.execute(f"""
            UPDATE batch_jobs SET output_filename = {ph()} WHERE id = {ph()}
        """, (output_filename, job_id))
        
        conn.commit()
