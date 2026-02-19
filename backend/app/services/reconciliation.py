import re
from typing import List, Dict, Any

class ReconciliationEngine:
    """
    Engine for matching Purchase Register entries against GSTR-2B data.
    """
    
    def __init__(self, tolerance: float = 1.0):
        self.tolerance = tolerance

    def normalize_invoice_number(self, invoice_num: str) -> str:
        """
        Normalize invoice number for fuzzy matching.
        Removes special characters, spaces, and leading zeros.
        """
        if not invoice_num:
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
        Match invoices from Purchase Register (pr_data) against GSTR-2B (gstr2b_data).
        
        Returns categorized results:
        - matched: Exact match (GSTIN + Invoice + Amount within tolerance)
        - mismatch: Partial match (GSTIN + Invoice match, but Amount mismatch)
        - missing_in_2b: Present in PR but not in GSTR-2B (Ineligible ITC)
        - missing_in_pr: Present in GSTR-2B but not in PR (Unclaimed ITC)
        """
        
        # Index GSTR-2B data for O(1) lookup
        # Key: (GSTIN, Normalized Invoice Number) -> List of invoices (in case of duplicates)
        gstr2b_index = {}
        processed_gstr2b_ids = set()
        
        for item in gstr2b_data:
            gstin = item.get('gstin', '').strip().upper()
            inv_num = self.normalize_invoice_number(item.get('invoice_number', ''))
            key = (gstin, inv_num)
            
            if key not in gstr2b_index:
                gstr2b_index[key] = []
            gstr2b_index[key].append(item)

        results = {
            "matched": [],
            "mismatch": [],
            "missing_in_2b": [],
            "missing_in_pr": []
        }

        # Iterate through Purchase Register
        for pr_item in pr_data:
            gstin = pr_item.get('gstin', '').strip().upper()
            inv_num = self.normalize_invoice_number(pr_item.get('invoice_number', ''))
            pr_amount = float(pr_item.get('taxable_value', 0) or 0) + float(pr_item.get('tax_amount', 0) or 0)
            
            key = (gstin, inv_num)
            
            # Find candidate matches in GSTR-2B
            candidates = gstr2b_index.get(key, [])
            
            match_found = False
            
            if candidates:
                # Candidates found (GSTIN + Invoice Number matched)
                # Check Amount
                for candidate in candidates:
                    gstr2b_amount = float(candidate.get('taxable_value', 0) or 0) + float(candidate.get('tax_amount', 0) or 0)
                    
                    diff = abs(pr_amount - gstr2b_amount)
                    
                    if diff <= self.tolerance:
                        # Exact Match
                        results["matched"].append({
                            "gstin": gstin,
                            "vendor_name": candidate.get('vendor_name') or pr_item.get('vendor_name'),
                            "invoice_number": pr_item.get('invoice_number'),
                            "invoice_date": pr_item.get('invoice_date'),
                            "pr_amount": pr_amount,
                            "gstr2b_amount": gstr2b_amount,
                            "difference": diff,
                            "status": "MATCHED",
                            "message": "Fully Reconciled"
                        })
                        processed_gstr2b_ids.add(candidate.get('id', candidate.get('invoice_number'))) # Track as processed
                        match_found = True
                        break # Stop checking candidates
                
                if not match_found:
                    # Found invoice number but amount mismatch
                    # Take the first candidate for comparison
                    candidate = candidates[0] 
                    gstr2b_amount = float(candidate.get('taxable_value', 0) or 0) + float(candidate.get('tax_amount', 0) or 0)
                    diff = pr_amount - gstr2b_amount
                    
                    results["mismatch"].append({
                        "gstin": gstin,
                        "vendor_name": candidate.get('vendor_name') or pr_item.get('vendor_name'),
                        "invoice_number": pr_item.get('invoice_number'),
                        "invoice_date": pr_item.get('invoice_date'),
                        "pr_amount": pr_amount,
                        "gstr2b_amount": gstr2b_amount,
                        "difference": diff,
                        "status": "MISMATCH",
                        "message": f"Amount Mismatch (Diff: ₹{diff:.2f})"
                    })
                    processed_gstr2b_ids.add(candidate.get('id', candidate.get('invoice_number')))
            
            else:
                # No match found in GSTR-2B
                results["missing_in_2b"].append({
                    "gstin": gstin,
                    "vendor_name": pr_item.get('vendor_name'),
                    "invoice_number": pr_item.get('invoice_number'),
                    "invoice_date": pr_item.get('invoice_date'),
                    "pr_amount": pr_amount,
                    "gstr2b_amount": 0,
                    "difference": pr_amount,
                    "status": "MISSING_IN_2B",
                    "message": "Invoice not found in GSTR-2B"
                })

        # Identify items in GSTR-2B that were NOT in PR
        for key, items in gstr2b_index.items():
            for item in items:
                # Check if this item's ID (or unique key) has been processed
                if item.get('id', item.get('invoice_number')) not in processed_gstr2b_ids:
                     gstr2b_amount = float(item.get('taxable_value', 0) or 0) + float(item.get('tax_amount', 0) or 0)
                     results["missing_in_pr"].append({
                        "gstin": item.get('gstin'),
                        "vendor_name": item.get('vendor_name'),
                        "invoice_number": item.get('invoice_number'),
                        "invoice_date": item.get('invoice_date'),
                        "pr_amount": 0,
                        "gstr2b_amount": gstr2b_amount,
                        "difference": -gstr2b_amount,
                        "status": "MISSING_IN_PR",
                        "message": "ITC Available but not claimed"
                    })

        return results
