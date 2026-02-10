# Implementation Plan: ITC Protection System (The "Control" Engine)

**Goal:** Build a "Kill Switch" system that prevents payment vouchers in ERPs (Tally/SAP) for non-compliant vendors.  
**Phase 1 Focus:** Tally Prime (TDL Plugin) + Core Descision Engine.

## User Review Required
> [!IMPORTANT]
> **Tally Integration Strategy:** We will use a "Hybrid" approach. The **Tally TDL** (Plugin) will handle the UI blocking inside Tally, but the *actual compliance check* will happen on our **Cloud Server**. This prevents the Tally file from becoming heavy and allows us to update rules (e.g., Rule 37A changes) without redeploying the plugin to every user.

## Phase 1: The "Kill Switch" Prototype (MVP)
**Objective:** Demonstrate a live payment block in Tally based on a simulated "Non-Filed" status.

### 1. The Decision Engine (Cloud Backend)
The "Brain" that accepts a GSTIN and returns `ALLOW` or `BLOCK`.
#### [NEW] [server.js](file:///Users/vignesh/New_idea/ITC_Protection_System/backend/server.js)
*   **Endpoint:** `/check-compliance`
*   **Input:** `{ gstin: "29ABCDE1234F1Z5", amount: 50000 }`
*   **Logic:**
    *   Check Rule 37A Database (simulated for MVP).
    *   Check GSTIN Status (Active/Cancelled).
*   **Output:** `{ status: "BLOCK", reason: "GSTR-3B Not Filed for Sept 2024" }`

### 2. The Tally Plugin (TDL Script)
The "Hand" that stops the user inside Tally.
#### [NEW] [payment_block.tdl](file:///Users/vignesh/New_idea/ITC_Protection_System/tally/payment_block.tdl)
*   **Trigger:** On "Voucher Creation" (Payment Voucher Type).
*   **Action:**
    1.  Extract Party GSTIN.
    2.  Send HTTP Request to our `server.js`.
    3.  If response is `BLOCK`:
        *   Display "System Error" Box: *"Compliance Check Failed: [Reason]"*.
        *   **Cancel** the save event (Prevent generating the voucher).

---

## Phase 2: The "Audit Defense" Layer
**Objective:** Generate the distinct proof document ("The Shield") for every cleared payment.

### 1. Snapshot Generator
#### [NEW] [certificate_gen.py](file:///Users/vignesh/New_idea/ITC_Protection_System/backend/certificate_gen.py)
*   **Library:** `reportlab` or `pdfkit`.
*   **Trigger:** When the API returns `ALLOW`.
*   **Output:** A signed PDF containing:
    *   Timestamp.
    *   Vendor Compliance Table (GSTR-1/3B filing dates).
    *   "Safe to Pay" Watermark.

---

## Phase 3: The "Override" Workflow (The CFO Dashboard)
**Objective:** Handle exceptions. Sometimes they *must* pay a blocked vendor (e.g., Utility bills, Critical supplies).

### 1. Web Dashboard
#### [NEW] [dashboard/index.html](file:///Users/vignesh/New_idea/ITC_Protection_System/frontend/index.html)
*   **Feature:** "Blocked Payments Queue".
*   **Action:** CFO clicks "Force Release".
*   **Result:** API updates the status to `ALLOW_ONCE` for that specific Transaction ID.
*   **Legal:** Pop-up waiver: *"I accept full liability for ITC Reversal risk."*

---

## Phase 4: Integration MVP (Pilot)
**Objective:** End-to-end test on a simulated environment.
1.  Set up a Mock Tally Application.
2.  Create 1 "Good" Vendor and 1 "Bad" Vendor (Rule 37A violator).
3.  **Test Case A:** Try to pay "Good Vendor" → Payment Success → PDF Generated.
4.  **Test Case B:** Try to pay "Bad Vendor" → Tally Screams "STOP" → Voucher Not Saved.

## Key Technical Decisions
*   **Backend:** Node.js (fast I/O for API) or Python (better for PDF/Data). *Recommendation: Node.js for the API speed.*
*   **Database:** PostgreSQL (for strict transactional integrity of the "Audit Log").
*   **Tally:** TDL (Tally Definition Language) capability to make HTTP calls (using `SimHTTP` or similar collection).
