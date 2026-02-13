"""
TaxPay Guard - CSV Parser for Batch Processing
Parses and validates CSV files containing vendor GSTINs
"""
import csv
import io
import re
from typing import List, Dict, Tuple


def validate_gstin(gstin: str) -> bool:
    """Validate GSTIN format (15 characters alphanumeric)"""
    if not gstin or len(gstin) != 15:
        return False
    # GSTIN format: 2 digit state code + 10 char PAN + 1 char entity + Z + 1 check digit
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[A-Z0-9]{1}$'
    return bool(re.match(pattern, gstin.upper()))


def parse_csv_content(content: bytes) -> Tuple[List[Dict], List[str]]:
    """
    Parse CSV content and extract vendor data.
    
    Expected columns: GSTIN, Vendor Name (optional), Amount (optional)
    
    Returns:
        Tuple of (valid_items, errors)
    """
    valid_items = []
    errors = []
    
    try:
        # Decode and parse CSV
        text_content = content.decode('utf-8-sig')  # Handle BOM
        reader = csv.DictReader(io.StringIO(text_content))
        
        # Normalize column headers (case-insensitive)
        if reader.fieldnames:
            reader.fieldnames = [f.strip().lower() for f in reader.fieldnames]
        
        for row_num, row in enumerate(reader, start=2):  # Start from 2 (after header)
            # Extract GSTIN (try multiple column name variations)
            gstin = None
            for col in ['gstin', 'gst', 'gst_number', 'gstin_number', 'vendor_gstin']:
                if col in row and row[col]:
                    gstin = row[col].strip().upper()
                    break
            
            if not gstin:
                errors.append(f"Row {row_num}: Missing GSTIN")
                continue
            
            if not validate_gstin(gstin):
                errors.append(f"Row {row_num}: Invalid GSTIN format '{gstin}'")
                continue
            
            # Extract optional vendor name
            vendor_name = ""
            for col in ['vendor_name', 'name', 'party_name', 'vendor', 'supplier', 'party_nam']:
                if col in row and row[col]:
                    vendor_name = row[col].strip()
                    break
            
            # Extract optional amount
            amount = 0.0
            for col in ['amount', 'value', 'invoice_amount', 'payment_amount']:
                if col in row and row[col]:
                    try:
                        amount = float(row[col].replace(',', '').strip())
                    except ValueError:
                        pass
                    break
            
            valid_items.append({
                'gstin': gstin,
                'vendor_name': vendor_name,  # Changed from party_name to match DB schema
                'amount': amount
            })
    
    except Exception as e:
        errors.append(f"Failed to parse CSV: {str(e)}")
    
    return valid_items, errors


def generate_sample_csv() -> str:
    """Generate a sample CSV template for users"""
    return """GSTIN,Vendor Name,Amount
33AABCU9603R1ZX,Good Vendor Pvt Ltd,50000
27AADCB2230M1Z5,Another Supplier,75000
29AABCT1234F1ZP,Test Company Ltd,100000"""
