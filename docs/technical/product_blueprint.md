# Product Blueprint: The "A to Z" Manual

> **What is this?** This is the Master Guide. It explains **How it Works** (Theory) and **How to Build It** (Action).

---

# Part 1: How It Works (The "Kill Switch" Flow)

Imagine a physical gate at the factory door.
*   **Current World:** The gate is open. Anyone can walk in (Get paid). You check who entered *at the end of the month*.
*   **Our World:** The gate is locked. To open it, you need a "Green Signal" from the Cloud.

### The 4-Step "Interception" Architecture

**1. The Trigger (Tally Prime)**
*   Accountant presses "Accept" on a Payment Voucher.
*   **INTERCEPTION:** Our plugin freezes Tally. It grabs the `GSTIN` and `Amount`.

**2. The Question (API Call)**
*   Tally secretly sends this data to our Cloud Server:
    *   `POST /check_vendor { "gstin": "29AABC...", "amount": 50000 }`

**3. The Brain (Python Logic)**
*   Our Server checks 3 things instantly:
    *   **Rule 37A:** Has this vendor filed GSTR-3B for the last 2 months?
    *   **Status:** Is their GSTIN Active?
    *   **TDS (Section 206AB):** Did they file Income Tax Returns for 2 years?

**4. The Verdict (The Response)**
*   **Green:** Server sends `{"action": "ALLOW"}`. Tally unfreezes. Voucher Saved.
*   **Red:** Server sends `{"action": "BLOCK", "reason": "STOP! GSTR-3B Not Filed."}`.
    *   **Action:** Tally shows a Pop-up Box. The "Accept" action is cancelled. The Accountant *cannot* pay.

---

# Part 2: The Logic (Business Rules)

We enforce **Two Layers of Defense**.

### Layer 1: ITC Protection (Rule 37A)
| Condition | Result | Message to User |
| :--- | :--- | :--- |
| **GSTR-3B Not Filed (> 2 Months)** | **BLOCK** | "STOP: Vendor has defaulted. 18% ITC Loss Risk." |
| **GSTIN Cancelled / Suspended** | **BLOCK** | "STOP: Invalid Registration. Invoice is fake." |
| **GSTR-3B Not Filed (1 Month)** | **WARN** | "WARNING: Vendor is late. Ask regarding status." |

### Layer 2: TDS Protection (Section 206AB)
| Condition | Result | Message to User |
| :--- | :--- | :--- |
| **ITR Not Filed (2 Years)** | **ALERT** | "ATTENTION: Deduct TDS at 20% (Double Rate)." |
| **PAN Status Invalid** | **BLOCK** | "STOP: PAN is invalid/inoperative." |

---

# Part 2.5: The "Money Logic" (Subscription & Workflow)

### 1. The Subscription Check (How we get paid)
Before checking the vendor, the API checks **YOU**.
1.  **Tally sends:** `POST /check_vendor { "api_key": "CLIENT_123", ... }`
2.  **Server checks:** Is `CLIENT_123` active? Has their license expired?
3.  **If Expired:** Server returns `{"action": "BLOCK", "reason": "License Expired. Renew at [YourWebsite]."}`.
    *   **Result:** The "Kill Switch" now protects *your revenue* too. They cannot use Tally for payments until they pay you.

### 2. The "CFO Override" (How HOLD becomes RELEASE)
Scenario: Vendor is flagged "HOLD" (Yellow), but CFO wants to pay anyway.

**Option A: The "Code" Method (Simple)**
1.  Tally Pop-up says: *"Blocked. Enter Manager Password to Override."*
2.  CFO types a secret code (e.g., `OVERRIDE_99`).
3.  Tally allows the save and logs: *"Overridden by Manager Code"*.

**Option B: The "Push Notification" Method (Advanced)**
1.  Tally Pop-up says: *"Blocked. Approval Request Sent to CFO."*
2.  Cloud Server sends a **WhatsApp/Email** to the CFO: *"Clerk is trying to pay ₹50k to Bad Vendor. Approve? [YES] [NO]"*
3.  CFO clicks `[YES]` on their phone.
4.  Clerk presses "Retry" in Tally -> It works.

*Note: For V1 (MVP), we use **Option A** (Password) because it is instant and easy to build.*

---

# Part 3: How We Build It (Step-by-Step)

## Step 1: The "Mock" Brain (Python)
We build a simple API that "pretends" to be the complex engine.
*   **File:** `backend/server.py`
*   **Tech:** FastAPI.
*   **Function:** Accepts a JSON, returns "Allow" or "Block" based on hardcoded rules (e.g., "Any GSTIN starting with 29 is BAD").

## Step 2: The Tally Connector (TDL)
We write the script that runs inside Tally.
*   **File:** `tally/itc_shield.tdl`
*   **Tech:** Tally Definition Language.
*   **Key Function:** `$$SysName:SafeHTTPCall`. This function allows Tally to talk to the Internet.

## Step 3: The Real Data (GSP Integration)
We replace the "Mock" brain with real Government Data.
*   **Provider:** Masters India or Vayana (Sandbox first).
*   **Action:** When API is hit, we query `GSP -> GSTR3B_Status`.

## Step 4: The Evidence (PDF Generation)
We generate the "Prevention Certificate".
*   **Tech:** Python `reportlab` library.
*   **Action:** If Blocked, generate `Certificate_Bad.pdf`. If Allowed, generate `Certificate_Good.pdf`. Save it to a folder.

---

# Part 4: The Deployment (How to install it)

1.  **The TCP File:** We compile our TDL code into a `.tcp` file (e.g., `Shield_v1.tcp`).
2.  **Delivery:** Email this file to the customer.
3.  **Installation:**
    *   Customer opens Tally.
    *   Goes to `F1 -> TDLs & Add-ons`.
    *   Selects our file.
    *   **Done.** The system is live.

---

# Part 5: Required Tech Stack
*   **Language:** Python 3.10+ (Backend logic).
*   **Framework:** FastAPI (High-speed API).
*   **Tally:** Tally Prime Edit Log 2.1+ (Client machine).
*   **Database:** PostgreSQL (To store audit logs).
