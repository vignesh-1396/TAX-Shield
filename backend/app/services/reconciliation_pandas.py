import pandas as pd
import re
from typing import List, Dict, Any

class ReconciliationEngine:
    """
    High-performance reconciliation engine using Pandas vectorized operations.
    ~100x faster than loop-based matching for large datasets.
    """
    
    def __init__(self, tolerance: float = 1.0):
        self.tolerance = tolerance

    def normalize_invoice_number(self, invoice_num: str) -> str:
        """
        Normalize invoice number for fuzzy matching.
        Removes special characters, spaces, and leading zeros.
        """
        if not invoice_num or pd.isna(invoice_num):
            return ""
        
        # Convert to string and uppercase
        norm = str(invoice_num).strip().upper()
        
        # Remove special characters (keep only alphanumeric)
        norm = re.sub(r'[^A-Z0-9]', '', norm)
        
        # Remove leading zeros
        norm = norm.lstrip('0')
        
        return norm

    def match_invoices(self, pr_data: List[Dict], gstr2b_data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Match invoices using Pandas vectorized operations.
        
        Returns categorized results:
        - matched: Exact match (GSTIN + Invoice + Amount within tolerance)
        - mismatch: Partial match (GSTIN + Invoice match, but Amount mismatch)
        - missing_in_2b: Present in PR but not in GSTR-2B (Ineligible ITC)
        - missing_in_pr: Present in GSTR-2B but not in PR (Unclaimed ITC)
        """
        
        # Convert to DataFrames
        df_pr = pd.DataFrame(pr_data)
        df_2b = pd.DataFrame(gstr2b_data)
        
        # Handle empty datasets
        if df_pr.empty and df_2b.empty:
            return {
                "matched": [],
                "mismatch": [],
                "missing_in_2b": [],
                "missing_in_pr": []
            }
        
        if df_pr.empty:
            # All 2B items are missing in PR
            df_2b['pr_amount'] = 0
            df_2b['gstr2b_amount'] = df_2b['taxable_value'].fillna(0) + df_2b['tax_amount'].fillna(0)
            df_2b['difference'] = -df_2b['gstr2b_amount']
            df_2b['status'] = 'MISSING_IN_PR'
            df_2b['message'] = 'ITC Available but not claimed'
            return {
                "matched": [],
                "mismatch": [],
                "missing_in_2b": [],
                "missing_in_pr": df_2b.to_dict('records')
            }
        
        if df_2b.empty:
            # All PR items are missing in 2B
            df_pr['pr_amount'] = df_pr['taxable_value'].fillna(0) + df_pr['tax_amount'].fillna(0)
            df_pr['gstr2b_amount'] = 0
            df_pr['difference'] = df_pr['pr_amount']
            df_pr['status'] = 'MISSING_IN_2B'
            df_pr['message'] = 'Invoice not found in GSTR-2B'
            return {
                "matched": [],
                "mismatch": [],
                "missing_in_2b": df_pr.to_dict('records'),
                "missing_in_pr": []
            }
        
        # Normalize columns
        df_pr['gstin_norm'] = df_pr['gstin'].fillna('').str.strip().str.upper()
        df_2b['gstin_norm'] = df_2b['gstin'].fillna('').str.strip().str.upper()
        
        df_pr['invoice_norm'] = df_pr['invoice_number'].fillna('').apply(self.normalize_invoice_number)
        df_2b['invoice_norm'] = df_2b['invoice_number'].fillna('').apply(self.normalize_invoice_number)
        
        # Calculate total amounts
        df_pr['pr_amount'] = df_pr['taxable_value'].fillna(0) + df_pr['tax_amount'].fillna(0)
        df_2b['gstr2b_amount'] = df_2b['taxable_value'].fillna(0) + df_2b['tax_amount'].fillna(0)
        
        # Merge on GSTIN + Normalized Invoice Number
        merged = pd.merge(
            df_pr,
            df_2b,
            on=['gstin_norm', 'invoice_norm'],
            how='outer',
            indicator=True,
            suffixes=('_pr', '_2b')
        )
        
        # Calculate difference
        merged['pr_amount'] = merged['pr_amount'].fillna(0)
        merged['gstr2b_amount'] = merged['gstr2b_amount'].fillna(0)
        merged['difference'] = merged['pr_amount'] - merged['gstr2b_amount']
        merged['abs_diff'] = merged['difference'].abs()
        
        # Categorize results
        results = {
            "matched": [],
            "mismatch": [],
            "missing_in_2b": [],
            "missing_in_pr": []
        }
        
        # MATCHED: Both sides present + Amount within tolerance
        matched = merged[
            (merged['_merge'] == 'both') & 
            (merged['abs_diff'] <= self.tolerance)
        ].copy()
        
        matched['status'] = 'MATCHED'
        matched['message'] = 'Fully Reconciled'
        matched['gstin'] = matched['gstin_norm']
        # Handle vendor_name safely
        if 'vendor_name_2b' in matched.columns:
            matched['vendor_name'] = matched['vendor_name_2b'].fillna(matched.get('vendor_name_pr', ''))
        else:
            matched['vendor_name'] = matched.get('vendor_name_pr', '')
        matched['invoice_number'] = matched['invoice_number_pr']
        matched['invoice_date'] = matched['invoice_date_pr']
        
        results['matched'] = matched[[
            'gstin', 'vendor_name', 'invoice_number', 'invoice_date',
            'pr_amount', 'gstr2b_amount', 'difference', 'status', 'message'
        ]].to_dict('records')
        
        # MISMATCH: Both sides present + Amount mismatch
        mismatch = merged[
            (merged['_merge'] == 'both') & 
            (merged['abs_diff'] > self.tolerance)
        ].copy()
        
        mismatch['status'] = 'MISMATCH'
        mismatch['message'] = mismatch['difference'].apply(lambda x: f"Amount Mismatch (Diff: ₹{x:.2f})")
        mismatch['gstin'] = mismatch['gstin_norm']
        mismatch['vendor_name'] = mismatch['vendor_name_2b'].fillna(mismatch['vendor_name_pr'])
        mismatch['invoice_number'] = mismatch['invoice_number_pr']
        mismatch['invoice_date'] = mismatch['invoice_date_pr']
        
        results['mismatch'] = mismatch[[
            'gstin', 'vendor_name', 'invoice_number', 'invoice_date',
            'pr_amount', 'gstr2b_amount', 'difference', 'status', 'message'
        ]].to_dict('records')
        
        # MISSING IN 2B: Only in PR
        missing_2b = merged[merged['_merge'] == 'left_only'].copy()
        missing_2b['status'] = 'MISSING_IN_2B'
        missing_2b['message'] = 'Invoice not found in GSTR-2B'
        missing_2b['gstin'] = missing_2b['gstin_norm']
        missing_2b['vendor_name'] = missing_2b['vendor_name_pr'] if 'vendor_name_pr' in missing_2b.columns else ''
        missing_2b['invoice_number'] = missing_2b['invoice_number_pr'] if 'invoice_number_pr' in missing_2b.columns else ''
        missing_2b['invoice_date'] = missing_2b['invoice_date_pr'] if 'invoice_date_pr' in missing_2b.columns else ''
        
        results['missing_in_2b'] = missing_2b[[
            'gstin', 'vendor_name', 'invoice_number', 'invoice_date',
            'pr_amount', 'gstr2b_amount', 'difference', 'status', 'message'
        ]].to_dict('records')
        
        # MISSING IN PR: Only in 2B
        missing_pr = merged[merged['_merge'] == 'right_only'].copy()
        missing_pr['status'] = 'MISSING_IN_PR'
        missing_pr['message'] = 'ITC Available but not claimed'
        missing_pr['gstin'] = missing_pr['gstin_norm']
        missing_pr['vendor_name'] = missing_pr['vendor_name_2b'] if 'vendor_name_2b' in missing_pr.columns else ''
        missing_pr['invoice_number'] = missing_pr['invoice_number_2b'] if 'invoice_number_2b' in missing_pr.columns else ''
        missing_pr['invoice_date'] = missing_pr['invoice_date_2b'] if 'invoice_date_2b' in missing_pr.columns else ''
        
        results['missing_in_pr'] = missing_pr[[
            'gstin', 'vendor_name', 'invoice_number', 'invoice_date',
            'pr_amount', 'gstr2b_amount', 'difference', 'status', 'message'
        ]].to_dict('records')
        
        return results
