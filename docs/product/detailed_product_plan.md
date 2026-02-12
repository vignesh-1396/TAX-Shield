# Product Plan: Pre-Payment GST Compliance Control (The "Kill Switch")

**Role:** Senior Enterprise SaaS Architect  
**Target:** Indian Mid-Market (Turnover ₹100Cr - ₹1500Cr)  
**Core Function:** Internal Control (IFC) for Accounts Payable

---

## Section 1: Product Philosophy

### 1. The Core Problem (CFO Perspective)
"I am terrified that I am paying 18% GST to vendors who are pocketing it instead of depositing it, creating a hidden liability that will hit me with 24% interest three years later when I can't recover the money."

### 2. What This Product IS and IS NOT
*   **It IS:** An **Internal Financial Control (IFC)** system. It is a "Gatekeeper" that physically stops money from leaving the bank account if compliance conditions are not met.
*   **It is NOT:** A Tax Filing Tool (like ClearTax/Winman), a Credit Rating Agency (like CRISIL), or a General Ledger.

### 3. Minimum Outcome to Prove Value
**The "Save":** The system must successfully **BLOCK** at least one payment voucher in Tally for a vendor who has actually defaulted on GSTR-3B, *before* the bank transfer file is generated.

---

## Section 2: Phased Build Plan

### PHASE 0: Validation (No Code)
**Goal:** Confirm the "Block" is acceptable to potential buyers.
*   **Artifacts to Validate:**
    1.  **The "Error Box" Mockup:** A screenshot of Tally showing a "Payment Blocked: GSTR-3B Violation" error preventing a voucher save. *Ask CAs: "Would you mandate this for your clients?"*
    2.  **The "Waiver" Process:** A mockup of the "CFO Override" report. *Ask CFOs: "If your AP team overrides a block, do you want a digitally signed log of who did it?"*
*   **Validation Signal:** A CFO says, "I want this installed because my AP team doesn't check the portal for every bill."

### PHASE 1: MVP - "Kill Switch" Control
**Objective:** Enforce compliance inside Tally.
*   **Architecture:**
    *   **Client Side:** Tally Prime with TDL Plugin (TCP file).
    *   **Server Side:** Node.js/Python API (The "Decision Engine").
    *   **Database:** PostgreSQL (Audit Logs, Cached Compliance Status).
*   **Backend Decision Engine logic:**
    *   Input: `GSTIN`, `Invoice_Date`, `Amount`.
    *   Logic: Check cached status -> If older than 24hrs, Live Fetch -> Compare Rule 37A.
    *   Output: `ALLOW` | `BLOCK_SOFT` (Warning) | `BLOCK_HARD` (Critical).
*   **Tally Integration (TDL):**
    *   Event: `On: Acceptance` of Payment Voucher.
    *   Action: HTTP POST to local/cloud API.
    *   Behavior: If `BLOCK_HARD`, return `FALSE` to `Form Accept`. Display `MsgBox`.
*   **Override Mechanism:**
    *   In Tally, add a custom UDF (User Defined Field): `Is_Compliance_Override` (Yes/No) and `Override_Reason` (Text).
    *   If `Is_Compliance_Override == Yes`, the API logs the event but returns `ALLOW`.
*   **MVP Exclusion:** No fancy dashboards, no email alerts, no PDF generation. Just the block.

### PHASE 2: Automation & Scale
**Objective:** Live data and reliable monitoring.
*   **Data Sourcing:** Integrate with a GSP (GST Suvidha Provider) like Masters India/Vayana for legal, stable API access to GSTR-3B filing dates. Do NOT screen-scrape GSTN (it breaks and is illegal).
*   **Vendor Monitoring:** Implement a "Nightly Sweep". Every night, check the filing status of all active vendors. Update the Cache.
*   **Notification:** If a vendor turns "Red" (Cancelled/Defaulted), email the AP Manager immediately *before* they even try to pay.

### PHASE 3: Enterprise Hardening
**Objective:** Audit defense.
*   **Audit Trail:** Immutable ledger of every API call: `Timestamp`, `User_IP`, `Tally_Serial_No`, `Decision`, `Override_Reason`.
*   **RBAC:** Separate web portal login for Auditors (Read-Only) vs. CFO (Admin).
*   **Security:** End-to-End verification. Ensure the TDL plugin is signed so it can't be tampered with.

---

## Section 3: Tally Integration Detail

### Interception Strategy
*   **Hook Point:** `[Form: Payment Color]` -> `On: Form Accept`.
*   **Safety:** Use a `System Formula` in TDL to validate.
    `[System: Formula]`
    `CheckCompliance : $$SysName:SafeHTTPCall ...`
*   **Method:** The TDL sends a compact JSON to your API. The API does the heavy lifting (logic, date comparisons). TDL just displays the result.

### Warnings vs. Hard Blocks
*   **Hard Block:** GSTIN Cancelled, GSTR-3B Not Filed > 2 months. (User *cannot* save voucher without Override).
*   **Warning:** GSTR-1 vs 3B mismatch, GSTR-3B Not Filed < 1 month. (User sees a popup but can proceed).

### Override UX
1.  User tries to save.
2.  **BLOCK** message appears: *"Vendor Non-Compliant. Rule 37A Risk. Contact Control."*
3.  User changes `Compliance Override` field to "Yes".
4.  User enters `Reason`.
5.  System forces a second API call to log this specific override action before saving.

### Risks
*   **Internet Down:** If API is unreachable, Tally will hang.
    *   *Mitigation:* TDL timeout of 3 seconds. Default to `ALLOW` but log "Check Failed - Internet" locally.
*   **Slow Response:** AP team gets frustrated.
    *   *Mitigation:* Cache decisions for 24 hours. Only fetch live if cache expired.

---

## Section 4: Data & Decision Logic

### Rule 37A Decision Logic (Simplified)
```python
def check_rule_37a(vendor_gstin, invoice_date):
    current_date = now()
    # 1. Check Registration
    if vendor.status in ['Cancelled', 'Suspended']:
        return BLOCK_HARD, "GSTIN is Inactive"

    # 2. Check Filing (Rule 37A)
    # Logic: Supplier must file GSTR-3B for FY X by Sept 30 of FY X+1
    # Operational Logic: Has supplier filed GSTR-3B for the previous month?
    last_month = get_previous_month(current_date)
    filing_status = get_gstr3b_status(vendor_gstin, last_month)

    if filing_status == 'NOT FILED' and days_overdue > 60:
         return BLOCK_HARD, "Critical: GSTR-3B Not Filed > 60 Days"
    elif filing_status == 'NOT FILED':
         return BLOCK_SOFT, "Warning: GSTR-3B Pending for Last Month"

    return ALLOW, "Compliant"
```

### Data Unavailability
*   If GSP API is down: Return `ALLOW_WITH_WARNING` ("Compliance Server Unreachable - Proceed with Caution"). Never completely stop business due to tech failure.

---

## Section 5: Audit & Legal Defensibility

### Why Defensible?
1.  **"Bonafide Check":** The log proves you checked compliance *at the time of payment*. This is the strongest defense against Section 16(2)(c) denial.
2.  **"Due Diligence":** The Override Log proves that non-compliance was an *exception*, not the rule, and was authorized by a human human.

### Disclaimers
*   *"This tool utilizes public data from GSTN. We do not guarantee the accuracy of government data."*
*   *"The decision to pay rests solely with the user. We are a data processor, not a legal advisor."*

---

## Section 6: Failure Modes (Be Brutal)

1.  **Tally Permissions:** Client's firewall blocks Tally from making outbound HTTP calls.
2.  **Latency:** API takes 5 seconds, AP clerk disables the plugin because "it slows me down."
3.  **False Positives:** GSTN portal is buggy and reports "Not Filed" when they actually part-paid. Client blocks a good vendor -> Relationship ruined.
4.  **Integration Fatigue:** CFO loves it, but the IT guy refuses to install a TCP file on 20 machines.
5.  **GSP Cost:** API calls cost money. If you poll too often, your margins vanish.
6.  **"Jugaad":** Accountants just bypass the Payment Voucher and pass a Journal Voucher instead (which you forgot to block).
7.  **Data Lag:** GSTN updates status 2 days later. You block a vendor who filed 1 hour ago.
8.  **Liability Fear:** A vendor sues your client for non-payment, and your client blames *your software*.
9.  **Complexity:** Small vendors don't file monthly (QRMP scheme). You block them wrongly because you expected a monthly return.
10. **The "Excel" Habit:** They pay via Tally, but the *real* approval happens on paper/Excel before Tally. The Tally entry is just record-keeping after the check is signed.

### Kill Signal
*   **The "Post-Facto" Reality:** If 80% of your clients enter data in Tally *after* writing the cheque, your product is useless as a generic "Kill Switch". You must pivot to "Cheque Printing Control" or "Bank File Generation Control".

---

## Section 7: Final Verdict

*   **Is this product needed?** **YES.** The pain of Rule 37A is real and financial. Manual checking is broken.
*   **Is the timing right?** **YES.** DGGI is aggressive, and e-Invoicing is maturing. The market is ready for "Control" over "Reporting".
*   **Execution Requirement:** You need a **"Distributor-Led"** approach. You cannot sell this direct-to-AP. You need the **Statutory Auditor** to mandate this tool to their clients as part of their "Internal Audit Check". Sell to the Auditor, not the Company.
