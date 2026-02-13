# Tally Integration Strategy: The "Add-On" Model

> **Core Concept:** We do **NOT** need to ask Tally Solutions (the parent company) for permission. Tally is an open platform. We build a "Plugin" (TCP file) that users install, just like adding an extension to Chrome.

## 1. How It Works (Technical)

We are not modifying Tally's source code. We are adding a layer *on top* of it.

### The "TCP" File
*   **What is it?** A small file (Tally Compiled Program) that we give to the customer.
*   **Installation:** The user goes to `Gateway of Tally -> F1 -> TDLs & Add-ons -> F4 -> Load TDL`.
*   **Time:** Takes 30 seconds. No IT expert needed.
*   **Effect:** Once loaded, our "Kill Switch" code becomes active inside their Tally.

### The Workflow (What the User Sees)
1.  **Accountant opens "Payment Voucher"** in Tally.
2.  Selects "Vendor A" and types "₹ 50,000".
3.  Presses **Enter** to save.
4.  **INTERCEPTION:** Our TDL script wakes up.
    *   It sends a silent signal to our Cloud API: *"Is Vendor A safe?"*
    *   Cloud API checks live GSTN data.
5.  **Reaction:**
    *   **Safe:** Voucher saves normally. (User sees nothing).
    *   **Risky:** A **Red Pop-up Box** appears in Tally: *"STOP! Vendor [Name] has not filed GSTR-3B for 2 months. Payment Blocked."*
6.  **Result:** The accountant *cannot* save the voucher (unless they have a special "Manager Password").

## 2. Commercial Strategy: "Direct to User"

We do not need to "partner" with Tally Solutions Pvt Ltd (Bangalore). We act as an independent software vendor (ISV).

### A. The "Direct" Route (Focus for V0)
*   **Target:** Companies already using Tally.
*   **Sales Pitch:** "Don't change your software. Just add our 'Safety Lock' to your existing Tally."
*   **Installation:** We send them the TCP file via email/WhatsApp. They install it. Done.

### B. The "Channel" Route (Scale)
*   **Partners:** There are 28,000+ "Tally Partners" (Resellers) in India.
*   **Incentive:** These partners visit clients daily to fix issues. We tell them: *"Sell our plugin to your 500 clients, keep 30% commission."*
*   **Why they will do it:** They are desperate for new things to sell to old clients.

## 3. Implementation Plan (For Us)

1.  **Hire TDL Developer (Freelance):**
    *   Skill: "Tally Definition Language (TDL)".
    *   Task: "Write a TDL that makes an HTTP POST request when the Payment Voucher 'Accept' button is pressed."
    *   Cost: ~₹30k - ₹50k for a robust script.
2.  **Cloud API (Python):**
    *   We build this. It receives the request and replies "Allow" or "Block".
3.  **Deploy:**
    *   Send the `.tcp` file to the user.

## 4. FAQ for Discussion

**Q: Does Tally allow this?**
A: **Yes.** Tally was built to be customized. Thousands of businesses use custom TDLs for invoices, payroll, etc.

**Q: Will it slow down Tally?**
A: We design it to "Fail Open". If our internet check takes more than 2 seconds, we auto-allow the transaction so the user isn't stuck. We then log a "Warning".

**Q: Can we sell this on "TallyShop"?**
A: Yes, eventually. TallyShop is like the "App Store" for Tally. But for now, selling directly is faster and keeps 100% margin.
