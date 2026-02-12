# 📋 GSTR-2B Reconciliation Implementation Plan (Phase 2)

## 🎯 Objective
Upgrade ITC Shield from "Vendor Due Diligence" to **"Full ITC Protection"** by reconciling user's purchase invoices against their official GSTR-2B data fetched from GSTN via GSP (Sandbox.co.in).

---

## 🏗️ Architecture Overview

The system needs 3 major new components:
1.  **Connect GSTIN Flow:** Allow users to link their GST portal account via OTP.
2.  **GSTR-2B Fetcher:** Download and store the user's GSTR-2B data for a given month.
3.  **Reconciliation Engine:** Compare uploaded invoices against the stored GSTR-2B data.

### Workflow
1.  User enters GST Username & clicks "Connect".
2.  System calls GSP → GSTN sends OTP to user.
3.  User enters OTP → System gets **Auth Token**.
4.  System calls `GET GSTR-2B` API using the token.
5.  System stores GSTR-2B invoices in `gstr_2b_data` table.
6.  When user uploads an invoice (Tally/Excel), system queries `gstr_2b_data`.
7.  **Match Found:** ✅ ITC Safe.
8.  **Mismatch/Not Found:** ❌ ITC at Risk (Alert User).

---

## 💾 Database Changes

We need new tables to store the user's GST credentials (token) and the downloaded GSTR-2B data.

### 1. `gst_credentials` table
Stores the session for the connected GSTIN.
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

### 2. `gstr_2b_data` table
Stores external invoice data downloaded from Govt.
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

---

## 🔌 API Integration (Sandbox.co.in GSP)

We will use the **GSP Taxpayer APIs** (requires OTP).

### Step 1: Request OTP
**Endpoint:** `POST /taxpayer/auth/request-otp`
- **Input:** `gstin`, `username`
- **Output:** `transaction_id` (OTP sent to mobile)

### Step 2: Verify OTP & Get Token
**Endpoint:** `POST /taxpayer/auth/verify-otp`
- **Input:** `otp`, `transaction_id`
- **Output:** `auth_token` (Valid for ~6 hours)

### Step 3: Fetch GSTR-2B
**Endpoint:** `GET /taxpayer/returns/gstr2b`
- **Input:** `financial_year`, `return_period`, `auth_token`
- **Output:** JSON list of all B2B invoices available in GSTR-2B.

---

## ⚡ Reconciliation Logic (The Core)

This logic runs when a user performs a **Compliance Check** on an invoice (Input: `Vendor GSTIN`, `Inv No`, `Inv Date`, `Amount`).

### Algorithm: `MatchInvoice(UserInvoice)`

1.  **Fetch Candidate:** Query `gstr_2b_data` where `gstin_supplier` == UserInvoice.VendorGSTIN.
2.  **Invoice Number Match:**
    *   *Strict:* `gstr2b.invoice_no == user.invoice_no`
    *   *Fuzzy:* Remove special chars (`/`, `-`, ` `) and leading zeros. Match `INV-001` with `INV001`.
3.  **Tax Amount Match:**
    *   If `abs(gstr2b.tax - user.tax) < 1.0` (Allow ₹1 rounding diff).
4.  **Result:**
    *   **MATCHED:** Vendor filed correctly. **(Green)**
    *   **MISMATCH_AMOUNT:** Vendor filed, but amount differs. **(Orange)**
    *   **NOT_FOUND_IN_2B:** Vendor has NOT filed this invoice yet. **(Red)**

---

## 📅 Implementation Roadmap

### Phase 2.1: Authentication (2 Weeks)
- [ ] Create `gst_credentials` table.
- [ ] Build "Link GSTIN" UI with Username/OTP form.
- [ ] Implement backend GSP Auth flow.

### Phase 2.2: Data Fetching (1 Week)
- [ ] Create `gstr_2b_data` table.
- [ ] Implement `fetch_gstr2b` background job.
- [ ] Store GSTR-2B JSON into DB rows.

### Phase 2.3: Reconciliation Engine (1 Week)
- [ ] Update `Decision Engine` to check `gstr_2b_data` table.
- [ ] Add "Reconciliation Status" to the API response.
- [ ] Update Alert Popup (e.g., "⚠️ Invoice Not in 2B").

---

## 💰 Resource Estimation
- **Development Time:** ~4 Weeks
- **Cost:**
    *   GSP API Costs: Higher (Taxpayer APIs are often charged per pull).
    *   Storage: Medium (Storing line-item invoice data increases DB size).
- **Complexity:** High (Handling OTP failures, GSP downtimes, fuzzy matching).

## ✅ Recommendation
Start with the **V1 (Vendor Due Diligence)** capabilities you have now. It provides 80% of value (stopping bogus vendors) with 20% of the effort.
Once you have 50-100 users, implement this **V2 (Reconciliation)** plan to upsell them to a "Pro" plan.
