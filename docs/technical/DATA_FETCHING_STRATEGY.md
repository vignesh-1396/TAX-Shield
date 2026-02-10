# Data Fetching Strategy: The Order of Operations

## Overview
Due to the frequent instability of the GSTN Portal, this system employs a **Data Availability Cascade**—a strict waterfall logic that prioritizes **Data Freshness** first, but defaults to **Availability** to prevent business stoppage, while maintaining legal defensibility.

---

## The Availability Cascade (Waterfall Logic)

The system must attempt to fetch data in the following prioritized order. It only moves to the next step if the previous step fails (Timeout / 5xx Error).

### 1. Primary: Live GSP Pipe (Preferred)
*   **Source:** Authorized GSP API (e.g., Masters India, ClearTax).
*   **Method:** Real-time API call during batch processing.
*   **Success Condition:** HTTP 200 OK + `timestamp` > Start of Day.
*   **Action:** Proceed to Rule Engine Logic.
*   **Status Code:** `SOURCE_LIVE_PRIMARY`

### 2. Secondary: Redundant GSP Pipe (Failover)
*   **Trigger:** Primary Pipe returns `503 Service Unavailable` or `TIMEOUT (>30s)`.
*   **Source:** Backup GSP (e.g., Cygnet, Microvista) or Direct API if available.
*   **Rationale:** Often the "pipe" (ASP-GSP link) is broken, but the GSTN core is active.
*   **Action:** Retry Verification.
*   **Status Code:** `SOURCE_LIVE_SECONDARY`

### 3. Tertiary: Local Time-Bounded Cache (Resilience)
*   **Trigger:** Both Primary and Secondary GSPs fail.
*   **Source:** Internal Database (`vendor_compliance_history`).
*   **Constraint:** Data must be less than **24 Hours Old**.
*   **Logic:** 
    *   IF `last_check_status` == 'Active' AND `last_check_timestamp` < 24h:
    *   **Result:** **PROVISIONAL PASS**.
    *   **UI Warning:** "Verified against Cache (GSTN Unreachable)".
*   **Rationale:** The risk of a vendor becoming non-compliant within 24 hours is statistically negligible compared to the cost of stopping payments.
*   **Status Code:** `SOURCE_CACHE_24H`

### 4. Quaternary: NIC E-Invoice Portal (The "Pulse Check")
*   **Trigger:** No valid Cache available (> 24h old).
*   **Source:** NIC E-Invoice / E-Way Bill Public Search (Separate infrastructure from GSTN Filing).
*   **Capability:** Can **ONLY** return `Active` or `Blocked` status. Cannot check Return Filing (3B).
*   **Action:**
    *   IF `Blocked` -> **STOP PAYMENT**. (Definite Risk)
    *   IF `Active` -> **CONDITIONAL HOLD**.
        *   *Message:* "Vendor is Active, but Filing Status Unknown. Portal Down."
        *   *Override:* Requires CFO "Pay at Own Risk" Waiver.
*   **Status Code:** `SOURCE_NIC_PULSE`

### 5. Final State: System Lockdown (Hard Stop)
*   **Trigger:** All external sources unavailable.
*   **Action:** **STOP PAYMENT**.
*   **User Message:** "External Compliance Systems Unreachable. Please try again in 15 minutes."
*   **Status Code:** `SOURCE_UNAVAILABLE`

---

## Summary Table

| Priority | Source | Data Quality | Defense Level | Action |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Live GSP | 100% (Real-time) | High | Validate Design Rules |
| **2** | Backup GSP | 100% (Real-time) | High | Validate Design Rules |
| **3** | Local Cache (<24h) | 99% (Near-time) | Medium-High | Provisional Release |
| **4** | NIC Portal | 50% (Status Only) | Low | Conditional Hold (Manager Override) |
| **5** | None | 0% | None | **HARD STOP** |
