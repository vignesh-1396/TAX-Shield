"""
TaxPay Guard - Purchase Register (PR) Parser
Parses Excel/CSV files for GSTR-2B Reconciliation.
"""
import io
import csv
import logging
from typing import List, Dict, Any, Tuple
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

def parse_purchase_register(file_content: bytes, filename: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Parse uploaded Purchase Register (Excel/CSV).
    
    Returns:
        Tuple[List[Dict], List[str]]: (valid_items, errors)
    """
    valid_items = []
    errors = []
    
    try:
        df = None
        
        # Determine file type and load into DataFrame
        if filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_content))
        elif filename.lower().endswith('.csv'):
            # Try to infer separator (comma or semicolon)
            try:
                df = pd.read_csv(io.BytesIO(file_content))
            except Exception:
                # Fallback to semicolon if simple comma parse fails
                df = pd.read_csv(io.BytesIO(file_content), sep=';')
        else:
            return [], ["Unsupported file format. Please upload .csv, .xlsx, or .xls"]

        # Normalize column headers: lowercase, strip, replace spaces with underscores
        df.columns = df.columns.astype(str).str.lower().str.strip().str.replace(' ', '_').str.replace('/', '_').str.replace('.', '')
        
        # Required columns (flexible matching)
        # We need: GSTIN, Invoice Number, Invoice Date, Taxable Value, Tax Amount
        
        column_map = {}
        
        # Map known variations to standard keys
        variations = {
            'gstin': ['gstin', 'gst_number', 'gstin_of_supplier', 'supplier_gstin'],
            'invoice_number': ['invoice_number', 'invoice_no', 'inv_no', 'document_number', 'doc_no'],
            'invoice_date': ['invoice_date', 'inv_date', 'document_date', 'doc_date'],
            'taxable_value': ['taxable_value', 'taxable_amount', 'net_amount', 'base_amount'],
            'tax_amount': ['tax_amount', 'total_tax', 'igst+cgst+sgst', 'gst_amount'],
            'vendor_name': ['vendor_name', 'party_name', 'supplier_name', 'name_of_supplier']
        }
        
        # Find matching columns
        for key, aliases in variations.items():
            found = False
            for col in df.columns:
                if col in aliases or any(alias in col for alias in aliases):
                    column_map[key] = col
                    found = True
                    break
            # Optional columns
            if not found and key not in ['vendor_name']:
                errors.append(f"Missing required column for '{key}'. Found columns: {list(df.columns)}")
                return [], errors

        # Process rows
        for index, row in df.iterrows():
            try:
                item = {}
                
                # GSTIN
                gstin = str(row.get(column_map.get('gstin'), '')).strip().upper()
                if not gstin or len(gstin) != 15:
                    continue # Skip invalid rows silently? Or log error? For large files, skip empty rows.
                    
                item['gstin'] = gstin
                
                # Invoice Number
                item['invoice_number'] = str(row.get(column_map.get('invoice_number'), '')).strip()
                
                # Invoice Date (Format YYYY-MM-DD or DD-MM-YYYY)
                raw_date = row.get(column_map.get('invoice_date'))
                if pd.notna(raw_date):
                    try:
                        dt = pd.to_datetime(raw_date)
                        item['invoice_date'] = dt.strftime('%Y-%m-%d')
                    except:
                        item['invoice_date'] = str(raw_date) # Keep as string if parsing fails
                        
                # Amounts
                try:
                    t_val = float(str(row.get(column_map.get('taxable_value'), 0)).replace(',', '')) if pd.notna(row.get(column_map.get('taxable_value'))) else 0.0
                    item['taxable_value'] = t_val
                except:
                    item['taxable_value'] = 0.0
                    
                try:
                    tax = float(str(row.get(column_map.get('tax_amount'), 0)).replace(',', '')) if pd.notna(row.get(column_map.get('tax_amount'))) else 0.0
                    item['tax_amount'] = tax
                except:
                   # If distinct column not found, maybe calculate? Or assume 0.
                   item['tax_amount'] = 0.0
                
                # Vendor Name (Optional)
                if 'vendor_name' in column_map:
                    item['vendor_name'] = str(row.get(column_map.get('vendor_name'), '')).strip()
                else:
                    item['vendor_name'] = ""
                
                valid_items.append(item)
                
            except Exception as e:
                errors.append(f"Row {index+2}: Error parsing - {str(e)}")
                
        return valid_items, errors

    except Exception as e:
        logger.error(f"File parsing error: {e}")
        return [], [f"File parsing failed: {str(e)}"]
