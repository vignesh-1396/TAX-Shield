# Implementation Plan - Phase 2: Tally Integration MVP

> **Goal:** Create a working "Kill Switch" prototype.
> **Outcome:** When a user saves a Payment Voucher in Tally, it hits our local API, and Tally blocks the save if the API says "BLOCK".

## User Review Required
> [!IMPORTANT]
> **Tally Developer License:** Verification of TDL scripts usually requires a licensed version of Tally or a Developer mode. We will write the script, but you (or a freelancer) need a Tally environment to test it.

## Proposed Changes

### 1. Python Backend (The Decision Engine)
We will build a lightweight **FastAPI** server to act as the "Brain".

#### [NEW] [server.py](backend/server.py)
*   **Technology:** Python / FastAPI / Uvicorn.
*   **Endpoints:**
    *   `POST /check_compliance`: Receives `{ "gstin": "...", "amount": 50000 }`.
    *   **Logic:**
        *   If `gstin` starts with "29" (Test Bad) -> Return `{"action": "BLOCK", "message": "GSTR-3B Not Filed"}`.
        *   Else -> Return `{"action": "ALLOW", "message": "Clean"}`.

### 2. Tally TDL Script (The Connector)
We will write the Tally Definition Language (TDL) script to intercept the "Accept" event.

#### [NEW] [itc_shield.tdl](tally/itc_shield.tdl)
*   **Technology:** Tally Definition Language.
*   **Key Components:**
    *   `[System: Formula]`: Define the HTTP Call to `http://localhost:8000/check_compliance`.
    *   `[Form: Payment Color]`: Hook into `On: Form Accept`.
    *   **Logic:**
        *   Trigger Formula on Save.
        *   Parse JSON response.
        *   If `action == "BLOCK"`, display Error Message and `Return: False` (Cancel Save).

## Verification Plan

### Automated Tests
*   **Test API:** Run `curl` commands against `localhost:8000` to verify JSON responses.

### Manual Verification (The "Hello World" Test)
1.  Run `server.py`.
2.  Load `itc_shield.tdl` into Tally Prime.
3.  Create a Payment Voucher for a vendor with GSTIN starting with "29".
4.  **Expectation:** Tally shows a "BLOCK" popup and refuses to save.
5.  Create a Payment Voucher for any other vendor.
6.  **Expectation:** Tally saves successfully.
