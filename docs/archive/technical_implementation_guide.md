# Technical Implementation Guide: ITC Protection System

**Role:** Senior Full-Stack Architect
**Objective:** Build a Pre-Payment Compliance Control System from scratch.
**Status:** MVP / Implementation Ready

---

## Section 1: High-Level System Architecture

### Components
1.  **Tally Integration Layer (Client):** A TDL (Tally Definition Language) plugin installed on the user's Tally implementation. It acts as the "Interceptor".
2.  **API Gateway / Backend (Node.js):** REST API that receives compliance check requests, processes logic, and returns decisions.
3.  **Core Database (PostgreSQL):** Relational DB to store vendor states, rules, and immutable audit logs.
4.  **Mock GSP Service:** For MVP, a simulated service to return GST data. Later replaced by actual GSP APIs (Vayana/Masters India).

### Tech Stack
*   **Backend:** Node.js (Express/Fastify) - Lightweight, handles high concurrency for API calls.
*   **Database:** PostgreSQL - Essential for ACID compliance and structured audit trails.
*   **Client:** Tally Prime (TDL).
*   **Hosting:** AWS Lambda (Serverless) or Docker on DigitalOcean (Cost-effective).

### Request Flow
1.  **Tally User** presses "Accept" on a Payment Voucher.
2.  **TDL Script** intercepts the event, extracts `GSTIN` and `Amount`.
3.  **TDL** makes a synchronous HTTPS POST request to `api.yourproduct.com/check`.
4.  **Backend** validates request -> Checks DB cache -> (Optional) calls GSP -> Rules Engine.
5.  **Backend** returns JSON: `{ "decision": "BLOCK", "reason": "Rule 37A" }`.
6.  **TDL** reads JSON.
    *   If `BLOCK`: Displays Alert, Cancels Save.
    *   If `ALLOW`: Allows Save.

---

## Section 2: Backend From Scratch

### Project Structure (Node.js)
```text
/backend
  /src
    /controllers    # Endpoint logic (complianceController.js)
    /services       # Business logic (rulesEngine.js, gspService.js)
    /models         # DB Models (Vendor, AuditLog)
    /middleware     # Auth, Validation, Logging
    /utils          # Helpers (idGenerator, dateUtils)
  app.js            # Express setup
  server.js         # Entry point
```

### Core API: The Check Endpoint
**POST** `/api/v1/compliance/check`
*   **Payload:**
    ```json
    {
      "client_id": "cust_001",
      "vendor_gstin": "29ABCDE1234F1Z5",
      "transaction_date": "2024-02-03",
      "amount": 50000.00,
      "voucher_number": "PV/24-25/001"
    }
    ```
*   **Response:**
    ```json
    {
      "decision": "BLOCK",   // ALLOW | BLOCK_SOFT | BLOCK_HARD
      "reason": "GSTR-3B Not Filed for Jan 2024 (Last Month)",
      "check_id": "chk_987654321",
      "timestamp": "2024-02-03T10:00:00Z"
    }
    ```

### Decision Engine Logic (Pseudocode)
```javascript
async function evaluateCompliance(gstin, amount) {
  // 1. Get Vendor Data (Cache or Fetch)
  const vendor = await VendorService.getOrFetch(gstin);

  // 2. Rule 1: GSTIN Status
  if (vendor.status !== 'Active') {
    return { decision: 'BLOCK_HARD', reason: `GSTIN is ${vendor.status}` };
  }

  // 3. Rule 2: Rule 37A (GSTR-3B Filing)
  const lastFiledDate = vendor.latest_gstr3b_date;
  const daysSinceFiling = dateDiff(today, lastFiledDate);

  if (daysSinceFiling > 60) {
    return { decision: 'BLOCK_HARD', reason: 'Critical: GSTR-3B overdue > 60 days' };
  }
  if (daysSinceFiling > 30) {
    return { decision: 'BLOCK_SOFT', reason: 'Warning: Last month GSTR-3B pending' };
  }

  return { decision: 'ALLOW', reason: 'Compliant' };
}
```

---

## Section 3: Database Design

### 1. Vendors Table
*   `gstin` (VPK, String 15)
*   `trade_name` (String)
*   `status` (Active/Cancelled)
*   `last_gstr3b_filing_date` (Date)
*   `last_synced_at` (Timestamp) - *For cache validity*

### 2. ComplianceChecks Table (The Transaction Log)
*   `check_id` (PK, UUID)
*   `client_id` (Indexed)
*   `gstin` (Indexed)
*   `amount` (Decimal)
*   `decision` (Enum: ALLOW, BLOCK_SOFT, BLOCK_HARD)
*   `reason` (Text)
*   `created_at` (Timestamp, Default Now)

### 3. AuditLogs (Immutable)
*   `log_id` (PK, UUID)
*   `check_id` (FK)
*   `action` (String) - e.g., "CHECK_INITIATED", "OVERRIDE_GRANTED"
*   `payload` (JSONB) - Store full request/response for legal proof.

---

## Section 4: Tally Integration (TDL)

### How TDL Works
Tally executes TDL scripts natively. You inject code into standard "Forms" (Screens).

### The Hook
We need to modify `[Form: Payment Color]`. This is the standard Payment Voucher screen.

### TDL Pseudocode
```tally
[#Form: Payment Color]
  ; Hook into the Accept Event
  On: Form Accept : Yes : Call : CheckComplianceRule

[Function: CheckComplianceRule]
  Variable : vGSTIN : String
  Variable : vAmount : String
  Variable : vServerResponse : String

  ; 1. Extract Data from current Voucher Object
  00 : Set : vGSTIN : $PartGSTIN  ; Assuming field name
  10 : Set : vAmount : $Amount

  ; 2. Call API (Using built-in SafeHTTPCall)
  ; Syntax: Method, URL, Header, Body, Encoding
  20 : Set : vServerResponse : $$SysName:SafeHTTPCall:"POST":"https://api.app.com/check":vHeader:vBody:"UTF-8"

  ; 3. Parse Response (String parsing in TDL is painful, use delimiters)
  30 : If : $$IsBlockDecision:vServerResponse
  40 :    MsgBox : "Compliance Block" : "Vendor is Non-Compliant. Payment Stopped."
  50 :    Return : False  ; Cancels the Save
  60 : Else
  70 :    Return : True   ; Allows the Save
```

***Note:** TDL JSON parsing is limited. For MVP, often easier to have API return simple text e.g., `BLOCK|Reason` or `ALLOW|OK` and split by `|`.

---

## Section 5: Security & Reliability

### Authentication
*   **MVP:** Static API Key compiled into the TCP (Tally Compiled File).
*   **Production:** Dynamic Token exchange. Tally makes a "Login" call with Client Creds to get a Session Token.

### Tampering
*   Compile TDL into `.TCP` format. This prevents users from reading/editing the source code.
*   Sign the response from Server with a hash to ensure Tally isn't tricked by a man-in-the-middle (advanced).

### Fail-Safe (The "Internet is Down" scenario)
*   **Logic:** If `SafeHTTPCall` returns Error/Timeout:
*   **Policy:** `Fail-Open` (Default Allow).
*   **Reason:** You cannot stop business because Wi-Fi is down. Log a "By-Pass" warning locally in Tally and sync later.

---

## Section 6: Deployment & Environment

### Environments
*   **Local:** `localhost:3000` + Local PostgreSQL. Tally running on Windows VM.
*   **Staging:** Simulated GSP responses.
*   **Production:** Real GSP connection.

### Monitoring
*   **Sentry:** For backend crash reporting.
*   **Logging:** Store all "Check" requests. Alert if `BLOCK` rate drops to 0 (indicates plugin disabled or removed).

---

## Section 7: MVP Cutline

### MUST BUILD
1.  Node.js API with 1 endpoint (`/check`).
2.  PostgreSQL DB with `Vendors` and `Logs`.
3.  Simulated Logic: "If GSTIN ends with 'Z', Return BLOCK". (To test Tally UI).
4.  Basic TDL that makes an HTTP POST and blocks Save on "BLOCK" response.

### MUST NOT BUILD
1.  User Dashboard / Frontend (Not needed for Tally blocking).
2.  Real GSP Integration (Use mocks).
3.  PDF Generation (Phase 2).
4.  Complex Auth (Use static API key).

---

## Section 8: Common Tech Failures

1.  **JSON Parsing in TDL:** Tally is terrible at JSON. **Fix:** Return pipe-delimited strings `BLOCK|Reason` for MVP.
2.  **Tally Freeze:** Synchronous HTTP calls freeze the UI. **Fix:** Set low timeouts (2-3 sec).
3.  **Voucher Mode vs Invoice Mode:** Tally has different "modes" for vouchers. **Fix:** Ensure hook applies to all modes.
4.  **SSL/TLS Issues:** Old Windows 7 machines with old Tally might fail HTTPS handshakes. **Fix:** Ensure Root Certs are updated or support HTTP for legacy (risky but real).
5.  **Concurrent Limits:** Node.js handles it, but DB connections might spike. **Fix:** Use a connection pool (pg-pool).
6.  **"Edit" Mode:** User modifies an old voucher. **Fix:** Ensure logic triggers on "Alter" as well as "Create".
7.  **Rounding Differences:** Tally amounts have high precision. **Fix:** Send exact string, don't round on client.
8.  **GSTIN Formatting:** Spaces/ dashes in Tally field. **Fix:** Sanitize/Trim GSTIN in backend.
9.  **Date Formats:** Tally sends dates strangely sometimes. **Fix:** Standardize to YYYY-MM-DD in TDL.
10. **Duplicate Checks:** User presses "Accept", gets error, fixes it, presses "Accept" again. **Fix:** Idempotency keys or simple stateless checks.
