# Master Execution Roadmap: ITC & TDS Protection System

> **Objective:** Go from "Validation" to "Live Pilot" in 30 Days.
> **Philosophy:** Sell first, Build second. Do not write complex code until a human says "I need this."

## 📅 Phase 1: The "Hustle" (Days 1-7)
**Goal:** Risk Reduction. Get 3 "Soft Commitments" before writing a line of TDL code.

*   [x] **Build "The Prop":** Generate Sample PDF Certificates (Good/Bad).
*   [x] **Validate Problem:** Confirm "Gap" with friendly contact (Accenture).
*   [ ] **The "Real" Meeting:** Get introduced to 1 Finance Head/CA.
    *   *Action:* Show the Prop. Ask: "If Tally blocked this payment automatically, is that worth ₹15k?"
*   [ ] **LinkedIn Setup:** Build the "CFO Magnet" profile to attract passive leads.

## 📅 Phase 2: The "Key" (Days 8-14)
**Goal:** Technical Proof. Make Tally verify *one* voucher.

*   [ ] **Hire TDL Expert:** Find a freelancer (Budget ₹5k-10k) for the "Connector".
    *   *Task:* "Write a TDL that hits `http://localhost:5000/check` when I save a Payment Voucher."
*   [ ] **Build "Mock" Server:**
    *   Create a simple Python API (FastAPI) that listens for Tally.
    *   Hardcode responses: If Vendor = "Bad" -> Return "BLOCK".
*   [ ] **The "Hello World" Demo:**
    *   Video: You type in Tally -> Pop-up appears -> You smile.

## 📅 Phase 3: The "Brain" (Days 15-21)
**Goal:** Real Data. Replace "Mock" with "Real".

*   [ ] **ITC Logic (Rule 37A):**
    *   Implement `decision_engine.py` to check GSTR-3B history.
    *   Rules: "If 3B not filed for > 2 months = BLOCK".
*   [ ] **TDS Expansion (New):**
    *   Implement "Section 206AB Check".
    *   Logic: "If IT Return not filed for 2 years = ALERT (Deduct 20%)."
*   [ ] **GSP Integration:**
    *   Connect to a real Data Provider (Masters India / Vayana / Sandbox).
    *   *Note:* Use a "Sandbox" (Free) account for dev.

## 📅 Phase 4: The "Pilot" (Days 22-30)
**Goal:** Live "BETA" with one friendly user.

*   [ ] **Install at "Friend's" Office:**
    *   Put the TCP file in their Tally.
    *   Run it in "Silent Mode" (Log only, don't block yet).
*   [ ] **Generate "Audit Report":**
    *   After 1 week, show them: "Here are 3 payments you made to risky vendors."
*   [ ] **The Close:**
    *   "Do you want me to turn the 'Blocker' on for next month?"

---

## 🛠️ Resource Requirements

| Component | Budget (Est.) | Skill Needed | Status |
| :--- | :--- | :--- | :--- |
| **Sales Props** | ₹0 | Design/Print | ✅ Ready |
| **TDL Script** | ₹5,000 - ₹10,000 | Tally Developer | ⏳ Hiring Soon |
| **Cloud Server** | ₹500/mo | Python/DevOps | ⏳ Pending |
| **GST Data API** | Free (Sandbox) | API Integration | ⏳ Pending |

## 🚀 Immediate Next Step
**Get that Introduction.** The feedback from a real CFO will tell us exactly which feature (ITC vs TDS) to build first in Phase 3.
