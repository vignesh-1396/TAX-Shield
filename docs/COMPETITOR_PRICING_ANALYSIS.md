# 🇮🇳 GST SaaS Competitor Pricing Research (India)

**Analysis Date:** February 2026
**Focus:** ITC Risk Management, Vendor Compliance Monitoring, and Partial GST Hold.
**Target Product:** "ITC Shield" (Vendor Compliance + Payment Control)

---

## 1. API Pricing (Market Estimates)

This section estimates the API costs for a SaaS builder (like `ITC Shield`) sourcing data from GSP providers (Sandbox, Masters India, etc.).

### GSTR-1 (Sales Data / Return Filing)
*   **Purpose:** Filing returns or fetching filed data.
*   **Cost Basis:** Per GSTIN per Month or Per API Call.

| Metric | Estimate (Low Volume) | Estimate (High Volume) |
| :--- | :--- | :--- |
| **Filing API** | ₹5 - ₹10 per return | ₹2 - ₹4 per return |
| **Status Check** | ₹0.50 - ₹1.00 per check | ₹0.10 - ₹0.25 per check |
| **Data Fetch** | ₹1 - ₹2 per call | ₹0.50 - ₹0.80 per call |

### GSTR-3B (Summary Return)
*   **Purpose:** Identifying "Filed vs Not Filed" status (Critical for Vendor Check).

| Metric | Estimate (Low Volume) | Estimate (High Volume) |
| :--- | :--- | :--- |
| **Filing API** | ₹5 - ₹10 per return | ₹2 - ₹4 per return |
| **Status Check** | **₹0.25 - ₹0.50 per check** | **₹0.05 - ₹0.15 per check** |

> **Key Insight for ITC Shield:** Your core "Vendor Check" relies heavily on **GSTR-3B Status Check**. This is your *highest volume* API but also the *cheapest*.

---

## 2. GSTR-2B / ITC Data Pricing (The Cost Driver)

This is the most expensive component because it involves fetching large datasets (purchase invoices).

*   **Pricing Model:** Usually "Per GSTIN Per Month" (unlimited fetches) OR "Per Pull" (each refresh costs money).

| Service | Estimated Cost | Notes |
| :--- | :--- | :--- |
| **GSTR-2B Fetch** | ₹10 - ₹30 per GSTIN/month | Includes JSON download of all invoices. |
| **Invoice-Level Data** | Included in above | Extracted from the JSON. |
| **Bulk Processing** | +20% premium | For high-speed async processing. |

*   **Cheapest Provider:** **Sandbox (Zoop)** often has aggressive startup tiers.
*   **Premium Provider:** **Clear (ClearTax)** and **Cygnet** charge a premium for reliability and "enriched" data.

---

## 3. SaaS Platform Pricing (End Customers)

What competitors charge their customers (SMEs/Enterprises).

### SME Plans (Turnover < ₹50 Cr)
*   **Pricing Range:** **₹15,000 - ₹50,000 per year**
*   **Includes:**
    *   3-5 GSTINs.
    *   Reconciliation (GSTR-2A vs 2B vs Books).
    *   Basic Vendor Compliance Report.
    *   Email Support.

### Mid-Market Plans (Turnover ₹50 Cr - ₹500 Cr)
*   **Pricing Range:** **₹1 Lakh - ₹5 Lakh per year**
*   **Includes:**
    *   Unlimited GSTINs (often negotiated).
    *   ERP Integration (Tally, SAP, Oracle).
    *   Custom Logic / partial automation.
    *   Multi-user roles (Maker/Checker).

### Enterprise Plans (Turnover > ₹500 Cr)
*   **Pricing Range:** **₹10 Lakh - ₹50 Lakh+ per year**
*   **Features:**
    *   Dedicated Server / On-Premise options.
    *   Custom APIs.
    *   White-glove support.

---

## 4. Competitor Comparison Table

| Provider | Pricing Level | Core Strength | Target Segment | Weakness |
| :--- | :--- | :--- | :--- | :--- |
| **Clear** (ClearTax) | **Premium** (High) | Brand Trust, Full Suite (ITR + GST + TDS) | Large Enterprises, CFOs | Very expensive, rigid contracts. |
| **Masters India** | **Medium** | API Reliability, Automating compliance | Mid-Market, Developers | UX can be complex for non-tech users. |
| **Sandbox** | **Low-Medium** | Developer Experience, Quick Integration | Startups, Fintechs | Support tiers vary for smaller accounts. |
| **Setu** | **Medium** | Modern API Infrastructure | Fintechs, Neobanks | Less focused on "GST Compliance", more on "Data". |
| **ITC Shield** | **Strategic** | **Payment Control (Stop/Hold)** | **SMEs using Tally** | Brand awareness, new entrant. |

---

## 5. Cost Benchmark Scenarios (Your Cost)

Estimated monthly API bill for `ITC Shield` based on user volume.
*Assumptions: 1 GSTR-2B fetch per GSTIN/month; 10 Vendor Checks per GSTIN/month.*

| Scenario | GSTR-2B Cost (₹20/GSTIN) | Vendor Checks (₹0.20/check) | Total API Cost | Revenue Potential (@₹10k/yr/user) | Margin |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **100 GSTINs** | ₹2,000 | ₹200 (1000 checks) | **₹2,200** | ₹83,000/mo | **97%** |
| **500 GSTINs** | ₹10,000 | ₹1,000 (5000 checks) | **₹11,000** | ₹4.1 Lakh/mo | **97%** |
| **1000 GSTINs** | ₹20,000 | ₹2,000 (10k checks) | **₹22,000** | ₹8.3 Lakh/mo | **97%** |

> **Conclusion:** API costs are negligible compared to SaaS subscription revenue. The specific API cost per unit is low.

---

## 6. Product Gap & Opportunity (The "Blue Ocean")

**What Competitors Do (Clear, Masters India, etc.):**
*   **"Post-Mortem" Report:** They show a report: *"These 50 invoices are not in GSTR-2B (Section 16(2)(aa) violation)."*
*   **Passive Aging:** They show an "Aging Report" for 180-day compliance (Rule 37), but they **don't stop you from paying**.
*   **Manual Follow-up:** You have to manually email the vendor based on the report.

**What ITC Shield Does (Differentiation):**
*   **"Pre-Payment" Control:** "Stop! Don't pay this invoice yet. Vendor is risky."
*   **Active Rule 37 Block:** If Invoice Date > 180 Days & Vendor Not Paid -> **Alert User before payment**.
*   **Partial Hold Logic:** "Pay 82%, hold 18% (Tax) until they file."
*   **Automated Release:** "Vendor filed yesterday. You can release the 18% now."

**The Value:** You are not just saving them time (reconciliation); you are **Saving Cash Flow** (preventing bad payments).

---

## 7. Final Proposed Pricing Models (Two-Tier Structure)

Based on your feedback, we will split the product into two distinct models.

### 🟢 Model 1: "Vendor Guard" (Basic Compliance)
*   **Focus:** Checking if the vendor is Active (GSTR-1) and Filing Returns (GSTR-3B).
*   **API Cost:** Very Low (~₹0.50 per check).
*   **User Action:** No OTP required. Just enter GSTIN.
*   **Recommended Price:** **₹4,999 / year** (or Free Freemium).
*   **Profit Margin:**
    *   100 Checks/mo = ₹50 cost.
    *   Revenue = ₹416/mo.
    *   **Margin: ~88%**

### 🛡️ Model 2: "ITC Shield Pro" (Full Reconciliation)
*   **Focus:** Matching Invoices vs GSTR-2B + 180-Day Rule.
*   **API Cost:** Higher (~₹20 per month per GSTIN).
*   **User Action:** Requires OTP Connection.
*   **Recommended Price:** **₹24,999 / year**.
*   **Profit Margin:**
    *   1 Fetch/mo = ₹20 cost.
    *   Revenue = ₹2,083/mo.
    *   **Margin: ~99%**

### � Why this works?
1.  **Low Friction Entry:** Sell Model 1 cheaply. It solves the immediate pain ("Is this vendor fake?").
2.  **High Value Upsell:** Once they trust you, upgrade them to Model 2 for the "Real Protection" (ITC Reversal Risk).


---

## 8. Summary

*   **API Costs are Low:** Your gross margins will be very high (>90%).
*   **Don't sell "Compliance":** Sell **"Cash Protection"**.
*   **Gap in Market:** Competitors focus on *Accountants* (Reconciliation). You should focus on *Business Owners/CFOs* (Payment Control).
