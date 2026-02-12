# Founder Memo: ITC Protection & Vendor Due Diligence System

## 1. Executive Summary
**Concept**: An enterprise-grade control system that protects businesses from GST Input Tax Credit (ITC) reversals caused by non-compliant vendors.
**Core Value**: We do not just automate checks; we provide **audit defensibility**.
**Primary Risk**: The structural risk is not the vendor running away with money; it is the **buyer's liability** to reverse ITC if the vendor defaults (Rule 37A).

## 2. The Problem: The "Excel + CA" Defense Gap
CFOs currently rely on a combination of Excel sheets and Chartered Accountants (CAs) to verify vendors.
*   **The Flaw**: In a court of law or during a GST audit, "My CA checked it" is not a defense. It lacks a timestamped, immutable record of due diligence.
*   **The Consequence**: When a vendor defaults (doesn't file GSTR-3B), the buyer is forced to reverse the ITC + Interest + Penalties. This directly hits the bottom line.
*   **The Psychology**: CFOs are not looking for "fraud detection" (which implies accusation); they want **liability protection**.

## 3. The Solution: Defensible Due Diligence
A system that sits before the payment run and generates **evidence of diligence**.

### Core Positioning
*   **External Name**: ITC Protection & Vendor Due Diligence System.
*   **Internal Concept**: "Compliance Shield".
*   **Language**:
    *   Avoid: "Fraud", "Background Check", "Credit Score".
    *   Use: "Liability Protection", "Due Diligence", "Compliance History".

### Unfair Advantage: Rule 37A Focus
We explicitly leverage **Rule 37A** of the CGST Rules. This rule creates the liability for the buyer but also defines the timeline for action. Our tool is the operational layer for Rule 37A compliance.

## 4. Product Strategy (V0)

### A. The "Moment of Use"
The system is used **just before the payment run**.
1.  AP Team uploads the payment batch list.
2.  System checks "Latest publicly available data as of [Timestamp]".
3.  **Gatekeeper Function**: Flags risky vendors (e.g., GSTR-3B not filed for 2 months).
4.  Finance Team holds payment for flagged vendors only.

### B. The "Auditor Artifact"
Per vendor or per batch, the system generates a **Due Diligence Certificate (PDF)**.
*   **Purpose**: To be attached to the audit file/voucher.
*   **Content**: "On [Date] at [Time], Vendor X was verified against GSTIN database. Status: Active. Filing Frequency: Regular. Risk Level: Low."
*   **Value**: This is the "shield" the CFO buys.

### C. Risk Scoring (The "Auditor View")
**Scale**: 0 to 100
*   **100 = High Risk** (Red Flag: Immediate payment hold)
*   **0 = Safe** (Green: Process payment)
*   Logic: High score indicates high probability of ITC reversal liability.

### D. Data Promise
*   **Honesty**: "Latest publicly available data." No false promises of "Real-time" if the GST portal is down.
*   **Timestamping**: Every data point is explicitly timestamped to protect the user ("We checked at 10:00 AM, the vendor defaulted at 4:00 PM - here is the proof we did our job").

## 5. Go-to-Market (GTM)

### Initial Ideal Customer Profile (ICP)
**Target**: **Exporters** & **Auto Ancillaries**.
*   **Why?**:
    *   Exporters: Claim refunds on ITC (LUT/Rebate). Any mismatch blocks MILLIONS in working capital.
    *   Auto Ancillaries: Tight margins, high volume of sub-vendors, strict audits.

### Liability Policy (Crucial for Trust)
*   **Stance**: Decision Support System.
*   **Guarantee**: We evidence *intent* and *diligence*. We do not guarantee vendor behavior.
*   **Liability**: Capped at subscription value.

## 6. Implementation Plan (V0 scope)
*   **Input**: Vendor GSTINs (Bulk CSV/Excel).
*   **Process**:
    *   Fetch GSTR-1 & GSTR-3B filing history (Public API/Scraper).
    *   Check Registration Status (Active/Suspended/Cancelled).
    *   Verify Legal Name vs Trade Name.
*   **Output**:
    *   Risk Score (High/Med/Low).
    *   Actionable Flag (Hold Payment / Release Payment).
    *   **Audit PDF** (The Artifact).
*   **Excluded from V0**: Penny drop (Bank verification) - offered as paid add-on later to reduce friction and dependency.
