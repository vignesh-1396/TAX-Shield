# CA Discussion Guide: Validating the "ITC Protection System"

**Objective:** Use this meeting to validate the legal "defensibility" of the tool and explore the CA's role as a channel partner.

---

## Part 1: Validating the Core Logic (The "Audit Shield")
*Roleplay: Ask the CA to put on their "Auditor Hat".*

### 1. The "Kill Switch" Rules
"We are automating the decision to block payments based on these triggers. If you were auditing a client, would you consider these rules **sufficient due diligence**?"

*   **Rule S1 (Cancelled):** "If we block a payment because the vendor is 'Cancelled', is there any scenario where this is wrong?"
*   **Rule S2 (Suspended):** "Does a 'Suspended' status legally mandate stopping payment, or is it just a warning?"
*   **Rule S3 (Non-Filer):** "We block payment if GSTR-3B is not filed for **2 months**. Is this aggressive enough? Should we block after just **1 month**?"

### 2. The "Evidence" (PDF Certificate)
"We generate a PDF time-stamped at the moment of payment. If a GST Notice comes 2 years later, will this PDF help you defend the client?"
*   *Show them the sample Certificate.*
*   **Key Question:** "What specific text or disclaimer must be on this PDF for you to accept it as valid audit evidence?"

---

## Part 2: Legal Liability (Protecting Yourself)
*Objective: Ensure you don't get sued if a client loses ITC.*

### 1. The Disclaimer Clause
"I want to sell this as a 'Decision Support Tool', not a guarantee. Is this disclaimer strong enough?"
*   *Draft:* "This report is based on public data as of [Timestamp]. The software provider is not liable for ITC reversals. The ultimate responsibility lies with the taxpayer under Section 16(2)(c) of the CGST Act."

### 2. The "Data Staleness" Risk
"The GST Portal data can be 2-3 days old. If we approve a vendor who was cancelled *yesterday* (but the portal didn't show it), can the client sue me?"
*   **Ask:** "Should I force users to re-login to the GST portal context every time, or is 'Last Known Status' acceptable for business continuity?"

---

## Part 3: Commercial & Partnership
*Objective: Turn the CA into a seller.*

### 1. The Value Proposition
"If your client uses this tool, does it makal **YOUR** internal audit easier?"
*   *Pitch:* "Instead of checking 500 invoices manually during the audit, you just check our 'Exception Report'."

### 2. Referral / Reseller Model
"I am pricing this at **₹15,000/year**. If you recommend this to your top 10 manufacturing clients, would you prefer:"
*   A flat referral fee (Commission)?
*   A bulk discount for your firm (e.g., you buy 10 licenses at ₹10k and bundle it into your retainer)?

---

## Part 4: The "Trap" Questions (To Test Their Depth)
*Ask these to see if the CA actually understands the pain point.*

1.  "Have any of your clients actually received a **Rule 37A notice** recently?" (If yes, drill down into *why*).
2.  "How do you currently verify if a vendor has filed their GSTR-3B before your client pays them?" (If they say "we check monthly", point out the gap: *Money leaves the bank weekly, you check monthly. It's too late.*)

---

## Part 5: The Vocabulary Cheat Sheet (Legal & Finance)
*Use these terms to sound like an expert partner, not just a software vendor.*

### A. Critical Law Sections (Memorize These)
| Section / Rule | What it means (Plain English) | How to use it in conversation |
| :--- | :--- | :--- |
| **Section 16(2)(c)** | **The Killer Clause.** A buyer cannot claim ITC unless the supplier has *actually paid* the tax to the government. | "Our tool specifically mitigates the **Section 16(2)(c) liability** by verifying filings *before* payment." |
| **Rule 37A** | **The Reversal Logic.** If a vendor doesn't file GSTR-3B by Sept 30 of next year, you must reverse ITC. | "We prevent the **Rule 37A triggers** at the source, rather than waiting for the annual reconciliation." |
| **Section 37 vs 38** | GSTR-1 (Sales) vs GSTR-2B (ITC Statement). | "We cross-reference the filing capability under **Section 37** to predict 2B eligibility." |
| **Companies Act Sec 134** | **IFC (Internal Financial Controls).** Directors are responsible for having checks in place to prevent fraud/loss. | "This tool serves as a robust **Internal Financial Control (IFC)** for your Director's Report." |

### B. Financial "Power Words"
| Instead of saying... | Say this... | Why? |
| :--- | :--- | :--- |
| "It stops you from losing money" | "It prevents **Working Capital Erosion**." | Sounds like a CFO problem. |
| "It checks the vendor" | "It performs **Counter-party Due Diligence**." | Sounds like a Bank/Audit term. |
| "If the vendor doesn't pay" | "If there is **Vendor Non-Compliance**." | Professional / Less accusatory. |
| "We keep a record" | "We maintain an **Immutable Audit Trail**." | Crucial for legal defense. |
| "You might have to pay later" | "It reduces **Contingent Liability**." | Something auditors hate to see on balance sheets. |

### C. The "Golden Sentence"
> "Sir/Ma'am, we are effectively deploying a **Section 16(2)(c) Firewall** that strengthens your **Internal Financial Controls (IFC)** and eliminates the **Contingent Liability** of doing business with non-compliant MSMEs."
