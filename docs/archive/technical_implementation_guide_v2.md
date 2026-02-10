# Technical Implementation Guide v2 (Revised)

**Role:** Senior Full-Stack Architect
**Objective:** Build a Pre-Payment Compliance Control System.
**Status:** Revised for Compliance & Audit Safety

---

## Section 1: Review of Architectural Changes
Based on the architectural review, the following critical changes have been applied:
1.  **Logic Update:** Shifted from "Day-based" (60 days) to "Period-based" (2 Return Periods) for Rule 37A accuracy.
2.  **Schema Hardening:** Added explicit Audit capabilities for Overrides.
3.  **Tally Safety:** Adopted a "Fail-Safe with Warning" policy to prevent blocking business operations during network outages.

---

## Section 2: Backend Architecture & Logic

### 1. Revised Rule Engine (Period-Based)
Rule 37A matches Input Tax Credit to the *Supplier's Filing*. The risk specifically arises when a supplier stops filing.

**Logic Definition:**
*   **BLOCK_HARD:** GSTIN Status is `Cancelled` OR `Suspended`.
*   **BLOCK_HARD:** GSTR-3B Not Filed for **3 or more** consecutive preceding tax periods.
*   **BLOCK_SOFT:** GSTR-3B Not Filed for **2** consecutive preceding tax periods.
*   **ALLOW:** Everything else.

**Pseudocode (Node.js):**
```javascript
async function evaluateCompliance(vendorData) {
  // 1. Status Check
  if (['Cancelled', 'Suspended'].includes(vendorData.status)) {
    return { decision: 'BLOCK_HARD', reason: 'GST Registration is Inactive' };
  }

  // 2. Return Period Check (Iterate last 3 months)
  const filings = vendorData.filing_history; // e.g. [{period: '012024', status: 'Filed'}, ...]
  const requiredPeriods = getLast3TaxPeriods(); // ['012024', '122023', '112023']
  let missedCount = 0;

  for (let period of requiredPeriods) {
    if (!filings.find(f => f.period === period && f.status === 'Filed')) {
      missedCount++;
    } else {
      break; // Stop counting on first successful filing (consecutive logic)
    }
  }

  if (missedCount >= 3) return { decision: 'BLOCK_HARD', reason: 'Critical: Non-filing for 3+ periods' };
  if (missedCount >= 2) return { decision: 'BLOCK_SOFT', reason: 'Warning: Non-filing for 2 periods' };
  
  return { decision: 'ALLOW', reason: 'Compliant' };
}
```

---

## Section 3: Database Design (Audit Ready)

### 1. ComplianceChecks (Transaction Log)
Updated to handle overrides explicitly.
*   `check_id` (PK, UUID)
*   `client_id` (Indexed)
*   `gstin` (Indexed)
*   `decision_system` (Enum: ALLOW, BLOCK_SOFT, BLOCK_HARD)
*   `decision_final` (Enum: ALLOW, BLOCK)
*   `is_overridden` (Boolean, Default: False)
*   `override_reason` (Text, Nullable)
*   `overridden_by_user` (String, Nullable)
*   `override_timestamp` (Timestamp, Nullable)

### 2. AuditLogs (Immutable)
*   `log_id` (PK)
*   `event` (CHECK_REQUEST | OVERRIDE_EVENT | BYPASS_EVENT)
*   `payload` (JSONB - Stores the snapshot of the decision)
*   `hash` (SHA256 of the payload for tamper-proofing)

---

## Section 4: Safe Tally Integration (TDL)

### Safety Pattern: "Verify First"
Directly blocking on "Save" can annoy users if the internet is slow.
**Improved Flow:**
1.  **Field Validations:** Check compliance when the user enters the `Party Name`.
2.  **Cache Result:** Store the result in a temporary variable.
3.  **Form Accept:** Only check the validation logic, do not make a *new* HTTP call if possible.

**Fail-Safe Policy (Network Failure):**
If the API times out (3 seconds) or returns 500:
1.  **Display Warning:** "Connection to Compliance Server Failed."
2.  **Action:** Allow the user to proceed (Fail-Open) but force them to enter a "Justification" in a local UDF field.
3.  **Sync:** Tally sends a backlog of "Bypassed Checks" to the server when connection restores.

**TDL Structure (Conceptual):**
```tally
[Function: CheckComplianceSafe]
  ; Set Timeout to 3 seconds
  00 : Set : vResponse : $$SysName:SafeHTTPCall:3000:"POST":...
  
  ; Handle Timeout/Error
  10 : If : $$IsEmpty:vResponse
  20 :    MsgBox : "Warning" : "Compliance Server Unreachable. Entering Offline Mode."
  30 :    Set : vDecision : "ALLOW_OFFLINE"
  40 : Else
  50 :    Set : vDecision : $$ExtractDecision:vResponse

  ; Handle Decision
  60 : If : vDecision == "BLOCK_HARD"
  70 :    MsgBox : "Restricted" : "Compliance Risk Detected. Payment Blocked."
  80 :    Return : False
  90 : Return : True
```

---

## Section 5: MVP Cutline (Strict)
**Phase 1 MVP Scope:**
*   **Must Have:**
    *   One-way integration: Tally -> Connectivity -> API.
    *   Hard Block logic for "Cancelled GSTIN".
    *   Fail-Open capability (so we don't halt business).
    *   Basic "Override" flag in DB (api-side only for now).
*   **Deferred (Phase 2):**
    *   Complex Tally UI for "Override Reason" entry (Just use a simple "Yes/No" toggle for MVP).
    *   Real-time GSP data (Use Mock Data).

---

## Section 6: UI Language Updates
**Risk:** Using legal terms like "Rule 37A" implies legal advice.
**Fix:** Use operational terms.

| Old String | New String |
| :--- | :--- |
| "Rule 37A Violation Found" | "Compliance Risk Detected" |
| "Illegal Vendor Status" | "inactive GST Registration Status" |
| "Safe to Pay" | "No Status Anomalies Detected" |

---

## Evaluation of Corrective Actions
1.  **Decision Logic:** **ADOPTED**. The "Period-based" logic is legally more accurate.
2.  **Override Schema:** **ADOPTED**. Essential for the "Audit Defense" value prop.
3.  **Tally Safety:** **ADOPTED**. The timeout-based "Fail-Open" policy is critical for user retention.
4.  **UI Language:** **ADOPTED**. Reduces liability risk for the SaaS company.
