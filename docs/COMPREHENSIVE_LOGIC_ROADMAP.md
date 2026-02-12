# 🛡️ Comprehensive ITC Protection Logic (V2 Roadmap)

This document outlines the **Unified Logic Architecture** that blends our existing "Vendor Health" checks with the upcoming "Invoice Reconciliation" (GSTR-2B) and "Payment Compliance" (Rule 37) capabilities.

## 🎯 The Goal
To move from **"Vendor Due Diligence"** (V1) to **"Total ITC Assurance"** (V2).

---

## 🏗️ The "Blended" Logic Hierarchy

We will process every invoice through **3 Layers of Defense**. If ANY layer fails, the ITC is at risk.

| Priority | Layer | Rule ID | The Check | Action | V1/V2? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **🛑 Critical Base** | **S1, S2** | **Is Vendor Active?** (Not Cancelled/Suspended) | **STOP** | ✅ **V1 (Ready)** |
| **2** | **👮 Classification** | **S4 (New)** | **Is Invoice in GSTR-2B?** (Govt Record) | **STOP** | 🚧 **V2 (Planned)** |
| **3** | **⚖️ Reco Check** | **H4 (New)** | **Does Tax Amount Match?** (18k vs 10k) | **HOLD** | 🚧 **V2 (Planned)** |
| **4** | **⏳ Aging Check** | **R37 (New)** | **Is Payment < 180 Days?** (Rule 37) | **ALERT** | 🚧 **V2 (Planned)** |
| **5** | **📉 Risk Analytics** | **S3, H1** | **Is Vendor a Defaulter?** (Habitual offender) | **HOLD** | ✅ **V1 (Ready)** |

---

## 🧩 Component Implementation Plan

### 1. Upgrade Tally TDL (The Missing Link)
Currently, Tally only sends `GSTIN` + `Amount`. To enable Rule 37 (180 days) and exact 2B matching, we MUST send more data.

**Required TDL Changes:**
```tally
;; OLD (V1) payload
"gstin": "27AAAA...",
"amount": 50000

;; NEW (V2) payload - REQUIRED
"gstin": "27AAAA...",
"amount": 50000,
"invoice_no": "INV/23-24/001",  <-- For GSTR-2B Matching
"invoice_date": "2024-01-01"    <-- For Rule 37 (180 Days)
```

### 2. Implement Rule 37 (180-Day Reversal) Logic
**The Law:** If you don't pay the vendor within 180 days of *Invoice Date*, you must reverse ITC with interest.

**The Logic:**
```python
def check_rule_37(invoice_date, payment_date=None):
    today = datetime.now()
    days_passed = (today - invoice_date).days

    if days_passed > 180 and not payment_date:
        return {
            "decision": "REVERSE_ITC",
            "reason": f"Payment pending for {days_passed} days (>180). Rule 37 Violation.",
            "risk": "CRITICAL"
        }
    return None
```
*Note: This requires us to track "Payment Status" in our SaaS, or receive the `VoucherDate` (Payment Date) from Tally.*

### 3. GSTR-2B Reconciliation Logic
**The Logic:**
1.  **Strict Match:** Try to find exact `Invoice No` + `Date` in GSTR-2B table.
2.  **Fuzzy Match:** If failed, try stripping special chars (e.g., `INV/001` -> `INV001`).
3.  **Tax Match:** Check if `GSTR2B.tax_amount == User.tax_amount`.

---

## 📅 Roadmap for Execution

### Phase 2.1: TDL Data Upgrade (Week 1)
*   [ ] Modify TDL to extract `VoucherDate`, `ReferenceDate` (Invoice Date), and `ReferenceNo` (Invoice No).
*   [ ] Update API endpoint `/compliance/check` to accept these new fields.

### Phase 2.2: GSTR-2B Fetching (Week 2-3)
*   [ ] Implement "Connect GSTIN" (OTP Flow).
*   [ ] Build background job to fetch GSTR-2B JSON from GSP.
*   [ ] Store data in `gstr_2b_data` table.

### Phase 2.3: The "Blended" Engine (Week 4)
*   [ ] Update `DecisionEngine` to run the 5-layer check shown above.
*   [ ] Return "Reconciliation Status" in the API response.

### Phase 2.4: 180-Day Monitor (Week 5)
*   [ ] Build a "Payment Aging" dashboard in the SaaS.
*   [ ] Alert users via Email/WhatsApp when invoices cross 150 days (Warning) and 180 days (Critical).

---

## ✅ Recommendation for NOW (V1 Launch)

**Launch V1 as "Vendor Due Diligence Tool".**
*   It protects against the **#1 Risk**: Bogus/Fake/Cancelled Vendors.
*   It protects against **Habitual Defaulters**.

**Market "V2 Pro" as "Full Reconciliation Suite".**
*   "Upgrade to Pro to automate GSTR-2B matching and 180-day compliance tracking."
