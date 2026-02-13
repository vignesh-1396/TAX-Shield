"""
CRUD Operations for GSTR-2B Data
Handles storing and retrieving GSTR-2B invoice data
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from app.db.session import get_connection, ph
import logging

logger = logging.getLogger(__name__)


def bulk_insert_gstr2b_invoices(
    user_id: str,
    invoices: List[Dict]
) -> int:
    """
    Bulk insert GSTR-2B invoices.
    
    Args:
        user_id: User ID
        invoices: List of invoice dicts from GSP
        
    Returns:
        Number of invoices inserted
    """
    try:
        inserted_count = 0
        
        with get_connection() as (conn, cursor):
            for inv in invoices:
                invoice_id = str(uuid.uuid4())
                
                cursor.execute(f"""
                    INSERT INTO gstr_2b_data (
                        id, user_id, gstin_supplier, invoice_no, invoice_date,
                        invoice_value, taxable_value, tax_amount, filing_status,
                        return_period, source, created_at
                    ) VALUES ({ph(12)})
                """, (
                    invoice_id,
                    user_id,
                    inv.get("supplier_gstin"),
                    inv.get("invoice_no"),
                    inv.get("invoice_date"),
                    inv.get("invoice_value"),
                    inv.get("taxable_value"),
                    inv.get("tax_amount"),
                    inv.get("filing_status", "Y"),
                    inv.get("return_period"),
                    "GSTR-2B",
                    datetime.now().isoformat()
                ))
                inserted_count += 1
            
            conn.commit()
        
        logger.info(f"Inserted {inserted_count} GSTR-2B invoices for user: {user_id}")
        return inserted_count
        
    except Exception as e:
        logger.error(f"Error bulk inserting GSTR-2B invoices: {str(e)}")
        return 0


def find_matching_invoice(
    user_id: str,
    supplier_gstin: str,
    invoice_no: str,
    invoice_date: Optional[str] = None
) -> Optional[Dict]:
    """
    Find a matching invoice in GSTR-2B data.
    
    Args:
        user_id: User ID
        supplier_gstin: Supplier GSTIN
        invoice_no: Invoice number
        invoice_date: Optional invoice date for exact match
        
    Returns:
        Invoice dict if found, None otherwise
    """
    try:
        with get_connection() as (conn, cursor):
            if invoice_date:
                # Exact match with date
                cursor.execute(f"""
                    SELECT id, gstin_supplier, invoice_no, invoice_date,
                           invoice_value, taxable_value, tax_amount, filing_status
                    FROM gstr_2b_data
                    WHERE user_id = {ph()}
                      AND gstin_supplier = {ph()}
                      AND invoice_no = {ph()}
                      AND invoice_date = {ph()}
                    LIMIT 1
                """, (user_id, supplier_gstin, invoice_no, invoice_date))
            else:
                # Match without date
                cursor.execute(f"""
                    SELECT id, gstin_supplier, invoice_no, invoice_date,
                           invoice_value, taxable_value, tax_amount, filing_status
                    FROM gstr_2b_data
                    WHERE user_id = {ph()}
                      AND gstin_supplier = {ph()}
                      AND invoice_no = {ph()}
                    LIMIT 1
                """, (user_id, supplier_gstin, invoice_no))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "supplier_gstin": row[1],
                    "invoice_no": row[2],
                    "invoice_date": row[3],
                    "invoice_value": row[4],
                    "taxable_value": row[5],
                    "tax_amount": row[6],
                    "filing_status": row[7]
                }
            return None
            
    except Exception as e:
        logger.error(f"Error finding matching invoice: {str(e)}")
        return None


def get_gstr2b_summary(user_id: str, return_period: str) -> Dict:
    """
    Get summary statistics for GSTR-2B data.
    
    Args:
        user_id: User ID
        return_period: Return period (MMYYYY)
        
    Returns:
        Summary dict with counts and totals
    """
    try:
        with get_connection() as (conn, cursor):
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_invoices,
                    SUM(invoice_value) as total_value,
                    SUM(tax_amount) as total_tax,
                    COUNT(DISTINCT gstin_supplier) as unique_suppliers
                FROM gstr_2b_data
                WHERE user_id = {ph()} AND return_period = {ph()}
            """, (user_id, return_period))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "total_invoices": row[0] or 0,
                    "total_value": float(row[1] or 0),
                    "total_tax": float(row[2] or 0),
                    "unique_suppliers": row[3] or 0
                }
            return {
                "total_invoices": 0,
                "total_value": 0.0,
                "total_tax": 0.0,
                "unique_suppliers": 0
            }
            
    except Exception as e:
        logger.error(f"Error getting GSTR-2B summary: {str(e)}")
        return {
            "total_invoices": 0,
            "total_value": 0.0,
            "total_tax": 0.0,
            "unique_suppliers": 0
        }


def delete_gstr2b_data(user_id: str, return_period: str) -> bool:
    """
    Delete GSTR-2B data for a specific period (before re-sync).
    
    Args:
        user_id: User ID
        return_period: Return period (MMYYYY)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_connection() as (conn, cursor):
            cursor.execute(f"""
                DELETE FROM gstr_2b_data
                WHERE user_id = {ph()} AND return_period = {ph()}
            """, (user_id, return_period))
            
            conn.commit()
            logger.info(f"Deleted GSTR-2B data for user: {user_id}, period: {return_period}")
            return True
            
    except Exception as e:
        logger.error(f"Error deleting GSTR-2B data: {str(e)}")
        return False


def get_supplier_invoices(user_id: str, supplier_gstin: str) -> List[Dict]:
    """
    Get all invoices from a specific supplier.
    
    Args:
        user_id: User ID
        supplier_gstin: Supplier GSTIN
        
    Returns:
        List of invoice dicts
    """
    try:
        with get_connection() as (conn, cursor):
            cursor.execute(f"""
                SELECT invoice_no, invoice_date, invoice_value, tax_amount,
                       filing_status, return_period
                FROM gstr_2b_data
                WHERE user_id = {ph()} AND gstin_supplier = {ph()}
                ORDER BY invoice_date DESC
            """, (user_id, supplier_gstin))
            
            invoices = []
            for row in cursor.fetchall():
                invoices.append({
                    "invoice_no": row[0],
                    "invoice_date": row[1],
                    "invoice_value": row[2],
                    "tax_amount": row[3],
                    "filing_status": row[4],
                    "return_period": row[5]
                })
            
            return invoices
            
            
    except Exception as e:
        logger.error(f"Error fetching supplier invoices: {str(e)}")
        return []

def get_invoices_by_period(user_id: str, return_period: str) -> List[Dict]:
    """
    Get all GSTR-2B invoices for a specific return period.
    
    Args:
        user_id: User ID
        return_period: Return period (MMYYYY)
        
    Returns:
        List of invoice dicts
    """
    try:
        with get_connection() as (conn, cursor):
            cursor.execute(f"""
                SELECT gstin_supplier, invoice_no, invoice_date, 
                       invoice_value, taxable_value, tax_amount, 
                       filing_status, source
                FROM gstr_2b_data
                WHERE user_id = {ph()} AND return_period = {ph()}
            """, (user_id, return_period))
            
            invoices = []
            for row in cursor.fetchall():
                invoices.append({
                    "gstin": row.get('gstin_supplier'),
                    "invoice_number": row.get('invoice_no'),
                    "invoice_date": row.get('invoice_date'),
                    "invoice_value": row.get('invoice_value'),
                    "taxable_value": row.get('taxable_value'),
                    "tax_amount": row.get('tax_amount'),
                    "filing_status": row.get('filing_status'),
                    "source": row.get('source')
                })
            
            return invoices
            
    except Exception as e:
        import traceback
        logger.error(f"Error fetching period invoices: {str(e)}\n{traceback.format_exc()}")
        return []
