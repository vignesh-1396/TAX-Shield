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
To enable Rule 37 (180 days) and exact 2B matching, we MUST send more data from Tally.

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

### 2. GSTR-2B Reconciliation Ecosystem
This system requires new database tables and API integration to fetch and store Govt data.

#### A. Database Schema
**`gst_credentials`**: Stores the session for the connected GSTIN.
```sql
CREATE TABLE gst_credentials (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    gstin VARCHAR(15) UNIQUE,
    username VARCHAR(50),
    auth_token TEXT,       -- Session token from GSTN
    token_expiry TIMESTAMP,
    is_active BOOLEAN
);
```

**`gstr_2b_data`**: Stores external invoice data downloaded from Govt.
```sql
CREATE TABLE gstr_2b_data (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    gstin_supplier VARCHAR(15), -- The vendor
    invoice_no VARCHAR(50),
    invoice_date DATE,
    invoice_value DECIMAL,
    taxable_value DECIMAL,
    tax_amount DECIMAL,         -- IGST + CGST + SGST
    filing_status VARCHAR(20),  -- 'Y' or 'N'
    return_period VARCHAR(10),  -- e.g., '022026'
    source VARCHAR(20) DEFAULT 'GSTR-2B'
);
CREATE INDEX idx_reconcile ON gstr_2b_data(gstin_supplier, invoice_no, invoice_date);
```

#### B. API Integration (Sandbox.co.in GSP)
We will use the **GSP Taxpayer APIs** (requires OTP).
1.  **Request OTP:** `POST /taxpayer/auth/request-otp`
2.  **Verify OTP:** `POST /taxpayer/auth/verify-otp` (Get Token)
3.  **Fetch GSTR-2B:** `GET /taxpayer/returns/gstr2b`

#### C. Reconciliation Logic (`MatchInvoice`)
1.  **Fetch Candidate:** Query `gstr_2b_data` where `gstin_supplier` == UserInvoice.VendorGSTIN.
2.  **Invoice Number Match:**
    *   *Strict:* `gstr2b.invoice_no == user.invoice_no`
    *   *Fuzzy:* Remove special chars (`/`, `-`, ` `) and leading zeros.
3.  **Tax Amount Match:** If `abs(gstr2b.tax - user.tax) < 1.0` (Allow ₹1 rounding diff).
4.  **Result:** `MATCHED` (Green), `MISMATCH_AMOUNT` (Orange), or `NOT_FOUND` (Red).

### 3. Implement Rule 37 (180-Day Reversal)
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

---

## � Security & Data Privacy (Critical)

Handling OTPs and GSTR-2B data requires **Banking-Grade Security**.

### 1. Zero-Storage for OTP
*   **Protocol:** We acting as a "Tunnel".
*   User enters OTP -> We send to GSP -> GSP gives Token.
*   **Policy:** We **NEVER** store the raw OTP in our database or logs.

### 2. Token Encryption (AES-256)
The `auth_token` in `gst_credentials` table grants access to user's tax data.
*   **Encryption:** The `auth_token` column must be **Encrypted at Rest** using AES-256.
*   **Key Management:** Decryption Text should be stored in Environment Variables (`GST_TOKEN_SECRET`), not in code.

### 3. Strict Access Control (Row Level Security)
*   **Risk:** User A seeing User B's invoices.
*   **Mitigation:** Every query to `gstr_2b_data` must strictly filter by `user_id`.
*   **Middleware:** Implement `RequireGSTScope` middleware that validates user ownership before fetching 2B data.

### 4. Data Retention Policy
*   GSTR-2B data is sensitive financial info.
*   **Policy:** We verify the data, store it for the active compliance period (e.g., FY + 6 years), and provide a "Delete My Data" button for users.

---

## �📅 Roadmap for Execution

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
