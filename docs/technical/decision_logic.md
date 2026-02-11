# Decision Logic & Operational Rules (V0)

## 1. Risk Decision Framework

### A. Decision Categories
We use **three** decision states (not two):

| Decision | Meaning | Action Required |
|----------|---------|-----------------|
| **RELEASE** | Safe to pay | No action needed |
| **HOLD** | Requires CFO review | Manual approval needed |
| **STOP** | Do not pay | Payment blocked |

### B. Explicit Decision Rules

#### STOP PAY (Immediate Block)
| Rule ID | Condition | Explanation Text |
|---------|-----------|------------------|
| S1 | GST Status = **Cancelled** | "Vendor's GST registration has been cancelled. ITC claim will be rejected." |
| S2 | GST Status = **Suspended** | "Vendor's GST registration is suspended by authorities. Payment blocked per Rule 37A." |
| S3 | GSTR-3B not filed for **last 2+ consecutive periods** | "Vendor has not deposited tax to Government for 2+ months. ITC reversal risk is HIGH." |

#### HOLD (CFO Review Required)
| Rule ID | Condition | Explanation Text |
|---------|-----------|------------------|
| H1 | GSTR-3B filed but **delayed by 30+ days** | "Vendor files returns late. Recommend CFO review before releasing payment." |
| H2 | GST registration is **less than 6 months old** | "New vendor. Limited compliance history available." |
| H3 | Mismatch between **Legal Name** and **Trade Name** (>30% difference) | "Name mismatch detected. Verify vendor identity before payment." |

#### RELEASE (Safe to Pay)
| Rule ID | Condition | Explanation Text |
|---------|-----------|------------------|
| R1 | GST Status = **Active** AND GSTR-3B filed on time for last 3 periods | "Vendor is compliant. Safe to process payment." |

---

## 2. Data Freshness & Liability Policy

### A. Data Source Declaration
**Every check must display:**
> "This verification is based on publicly available GST data as of **[DD-MMM-YYYY HH:MM IST]**."

### B. Staleness Warnings
| Data Age | Warning Level | Display Message |
|----------|---------------|-----------------|
| < 24 hours | None | (No warning) |
| 24–72 hours | Yellow | "⚠️ Data is 2 days old. GST portal may have newer information." |
| > 72 hours | Red | "🚫 Data is stale. Recommend manual verification on GST portal." |

### C. Liability Disclaimer (Mandatory on every PDF)
> **Disclaimer:**  
> This certificate is a **decision support tool** based on publicly available data. It does not guarantee vendor behavior or tax compliance. The buyer retains full responsibility for ITC claims under Section 16(2)(c) of the CGST Act. This report evidences due diligence performed as of the timestamp mentioned above.

---

## 3. Role-Based Operational Workflow

### A. User Roles
| Role | Responsibility | Access Level |
|------|----------------|--------------|
| **AP Clerk** | Upload payment batch | Upload only |
| **Finance Manager** | Review flagged vendors | View + Override HOLD |
| **CFO** | Final approval for STOP/HOLD cases | View + Override + Audit trail |

### B. Daily Workflow (V0)
```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Upload (AP Clerk)                                   │
│ - Upload Excel with columns: Vendor Name, GSTIN, Amount     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Automated Check (System)                            │
│ - Fetch GST data for each GSTIN                             │
│ - Apply decision rules (S1-S3, H1-H3, R1)                   │
│ - Generate risk flags                                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Review Dashboard (Finance Manager)                  │
│ - RELEASE: Auto-approved (green)                            │
│ - HOLD: Requires review (yellow)                            │
│ - STOP: Blocked (red)                                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: CFO Approval (if HOLD/STOP exists)                  │
│ - CFO reviews explanation text                              │
│ - Can override HOLD → RELEASE (with reason)                 │
│ - Cannot override STOP (hard block)                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Evidence Generation (System)                        │
│ - Generate "Due Diligence Certificate" PDF                  │
│ - Email to CFO + Archive in system                          │
│ - Attach to payment voucher in ERP                          │
└─────────────────────────────────────────────────────────────┘
```

### C. Usage Frequency
| Activity | Frequency | User |
|----------|-----------|------|
| Payment batch upload | Weekly (or per payment cycle) | AP Clerk |
| Review flagged vendors | Weekly | Finance Manager |
| Audit trail review | Monthly | CFO |
| Compliance report generation | Quarterly (for statutory audit) | CFO |

---

## 4. V0 Scope Boundaries

### ✅ IN SCOPE (V0)
- Upload Excel with GSTINs
- Check GST status (Active/Cancelled/Suspended)
- Check GSTR-3B filing history (last 3 periods)
- Generate timestamped PDF certificate
- Dashboard with STOP/HOLD/RELEASE flags

### ❌ OUT OF SCOPE (V0)
- Penny drop / Bank account verification (V1 feature)
- Integration with ERP systems (manual export for now)
- Email alerts (manual download for now)
- Historical trend analysis (V1 feature)
- ML-based risk scoring (rule-based only for V0)

---

## 5. Sample Decision Outputs

### Example 1: STOP PAY
```
Vendor: ABC Traders Pvt Ltd
GSTIN: 29AABCU9603R1ZX
Status: CANCELLED
Decision: 🚫 STOP PAY

Reason: "Vendor's GST registration has been cancelled. 
ITC claim will be rejected per Section 16(2)(c)."

Data as of: 03-Feb-2026 10:30 IST
```

### Example 2: HOLD
```
Vendor: XYZ Industries
GSTIN: 27AAPFU0939F1ZV
Status: ACTIVE
GSTR-3B Filing: Delayed by 45 days (last period)
Decision: ⚠️ HOLD – CFO REVIEW

Reason: "Vendor files returns late. Recommend CFO review 
before releasing payment."

Data as of: 03-Feb-2026 10:30 IST
```

### Example 3: RELEASE
```
Vendor: DEF Exports Ltd
GSTIN: 33AABCD1234E1Z5
Status: ACTIVE
GSTR-3B Filing: On-time for last 3 periods
Decision: ✅ RELEASE

Reason: "Vendor is compliant. Safe to process payment."

Data as of: 03-Feb-2026 10:30 IST
```
