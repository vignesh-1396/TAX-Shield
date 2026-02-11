# Commercial Strategy & Financial Roadmap
## Combined Master Protocol

> **Consolidated From:** pricing_strategy.md, investor_pricing_strategy.md, budget_estimates.md
> **Date:** Feb 2026

---

# Part 1: Pricing Strategy (The Revenue Engine)

## 1. The Core Philosophy
**Positioning:** Do not sell "Accounting Software". Sell "Audit Insurance".
**The Value Equation:**
*   **The Risk:** Buying ₹1L from a bad vendor = **₹18,000 Loss** (18% ITC Reversal).
*   **The Solution:** Pay us **₹15,000/year** to prevent that loss.
*   **ROI:** Immediate positive ROI on the *first* blocked bad payment.

## 2. Pricing Tiers

### A. Core Defense (Target: Small Mfg/SME)
*   **Price:** **₹ 24,000 / year** (Discounted to ₹ 15,000 for early adopters).
*   **Features:**
    *   Tally Plugin ("Kill Switch").
    *   Unlimited Real-time Checks.
    *   Basic PDF Certificates.
    *   1 Admin User.

### B. Audit Shield (Target: Mid-Market ₹20cr+)
*   **Price:** **₹ 49,000 / year**.
*   **Features:**
    *   **Audit Defense Pack:** "Bona Fide" Certificates for Rule 37A.
    *   **CFO Workflow:** Override Dashboard & Reason Logging.
    *   **History:** 8-Year Data Retention.
    *   **Priority Support:** Direct WhatsApp Line.

### C. Enterprise GRC (Target: ₹100cr+)
*   **Price:** **₹ 1,50,000+ / year**.
*   **Features:**
    *   Custome ERP Integration (SAP/Oracle).
    *   Multi-GSTIN Group Dashboard.
    *   Dedicated Account Manager.

## 3. Launch Strategy: "The Founding Member"
*   **Anchor Price:** Display ₹ 49,000/year public price.
*   **Offer:** "First 50 Customers pay **₹ 24,000** and get Tier 2 features for Life."
*   **Goal:** Rapid cash flow to fund development.

---

# Part 2: The 4-Tier Strategic Budget Map

> **Bottom Line Up Front**
> *   **Total Capital Required:** ₹15,000 – ₹55,000
> *   **Absolute Hustler Mode (Do it yourself):** ~₹15,000
> *   **Outsourced Mode (Hire for Tally/TDL):** ~₹55,000
> *   **Detailed Budget Breakdown:** See below.

## 1. Comparative Strategy Table

| Feature | **Tier 0: The Hustle** | **Tier 1: Min Viable** | **Tier 2: The Pro** | **Tier 3: The Scale** |
| :--- | :--- | :--- | :--- | :--- |
| **Capital Required** | **₹ 0 (Free)** | **₹ 50,000** | **₹ 1,00,000** | **₹ 2,00,000** |
| **Goal** | Validate Logic & Pitch | Functional Proto | Stable Business | Aggressive Growth |
| **Backend** | Localhost (Your Laptop) | DigitalOcean Droplet | AWS Reserved Instance | Auto-Scaling Cloud |
| **Tally Connect** | **Manual/Mock** | Basic Freelancer | **Senior Expert** | Professional Agency |
| **Data Source** | Mock Data / Scraped | Basic API Plan | **Official GSP Plan** | Enterprise GSP Plan |
| **Legal** | None (Personal Risk) | MSME Reg Only | **Liability Contract** | Pvt Ltd Company |
| **Dev Method** | DIY (You code all) | Outsourced Core | Outsourced All | Dedicated Team |
| **Launch Scale** | Demo Only | 5 Beta Users | 50 Paid Users | Market Leader |

---

## 2. Execution Phases

### A. Tier 0: The "Free Cost" Build (Immediate Action)
**Objective:** Build the engine *before* buying the car. Prove it works to investors/partners.
*   **Cost:** ₹0 (Uses your "Sweat Equity").
*   **Infrastructure:**
    *   Run Python backend on **Localhost**.
    *   Database: **SQLite** (Free, local).
    *   GST Data: Use **Mock JSONs** (Simulate valid/invalid GSTINs) or public scraping (careful usage).
*   **Tally Integration:**
    *   *Do not hire yet.*
    *   Write a "Fake Tally" script: A Python script that *pretends* to be Tally sending a voucher to your API.
    *   Verify the API rejects the bad voucher.
*   **Deliverable:** A video demo showing: "Invoice Entered -> API Checked -> Risk Detected -> Blocked".

### B. Tier 1: Minimum MVP (₹ 50,000)
**Objective:** The first real customer installation.
*   **Spends:**
    *   **₹ 30,000:** TDL Freelancer (Basic connector).
    *   **₹ 15,000:** GSP API Credits (Small pack).
    *   **₹ 5,000:** Cheap VPS Hosting (3 months).
*   **Risk:** System might be buggy; no legal protection.

### C. Tier 2: Professional Alpha (₹ 1,00,000) - **RECOMMENDED**
**Objective:** Stable, sleep-well-at-night business.
*   **Spends:**
    *   **₹ 40,000:** Senior TDL Developer (Error handling, UI in Tally).
    *   **₹ 20,000:** Pre-paid Server & Official APIs (1 Year).
    *   **₹ 10,000:** Lawyer (Liability Shield Agreement).
    *   **₹ 30,000:** Buffer/Marketing.
*   **Advantage:** You survive a server crash or a legal threat.

### D. Tier 3: Growth Mode (₹ 2,00,000)
**Objective:** Sales Velocity.
*   **Spends:**
    *   **₹ 1.0L:** Product (Same as Tier 2).
    *   **₹ 50,000:** **Sales Commision** (Pay agents to sell for you).
    *   **₹ 50,000:** Content Marketing / Workshops for CAs.
*   **Advantage:** You don't hunt customers; they come to you.

---

## 3. Financial Projections (ROI)

| Tier | Breakeven Sales (at ₹15k) | Risk Level | Time to Market |
| :--- | :--- | :--- | :--- |
| **Tier 0** | N/A (Demo only) | High (Vaporware) | 2 Weeks |
| **Tier 1** | 4 Customers | Medium (Bugs) | 6 Weeks |
| **Tier 2** | 7 Customers | Low (Stable) | 8 Weeks |
| **Tier 3** | 14 Customers | Low (Aggressive) | 8 Weeks |


---

# Part 3: Investor Pitch Highlights

## Why Invest?
1.  **Stickiness:** Once installed in Tally, it becomes part of the *payment workflow*. Removing it requires changing internal processes. Retention > 95%.
2.  **Negative Churn:** As clients grow, they move to higher tiers (Audit Shield).
3.  **LTV:CAC Ratio:**
    *   LTV: ₹ 2 Lakhs+ (5 years @ ₹40k avg).
    *   CAC: ₹ 5,000 (Direct Sales).
    *   Ratio: **40:1** (Exceptional).

## The Competitive Moat
*   **Others (ClearTax, Vayana):** Focus on *Post-Facto Reporting* (Reconciliation).
*   **Us:** Focus on *Pre-Payment Control* (The "Kill Switch"). We stop the money from leaving the bank.

---
