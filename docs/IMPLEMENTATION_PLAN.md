# ITC Shield - Complete Production Implementation Plan

> **Goal:** Production-ready SaaS with real decision logic + Tally integration  
> **Timeline:** 6-8 weeks  
> **Budget:** ₹80,000 - ₹1 Lakh

---

## System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      TALLY (Customer Site)                      │
│  ┌──────────────┐                                              │
│  │ TDL Plugin   │──── HTTPS POST ────┐                         │
│  │ (Freelancer) │                    │                         │
│  └──────────────┘                    ▼                         │
└──────────────────────────────────────┼─────────────────────────┘
                                       │
                   ┌───────────────────▼───────────────────┐
                   │           CLOUD (Render.com)          │
                   │  ┌─────────────────────────────────┐  │
                   │  │       FastAPI Backend           │  │
                   │  │  ┌───────────────────────────┐  │  │
                   │  │  │     GSP Data Fetcher      │  │  │
                   │  │  │  (Waterfall: GSP→Cache)   │  │  │
                   │  │  └───────────────────────────┘  │  │
                   │  │  ┌───────────────────────────┐  │  │
                   │  │  │     Decision Engine       │  │  │
                   │  │  │    S1-S3, H1-H3, R1       │  │  │
                   │  │  └───────────────────────────┘  │  │
                   │  │  ┌───────────────────────────┐  │  │
                   │  │  │    PDF Generator          │  │  │
                   │  │  │  (Due Diligence Cert)     │  │  │
                   │  │  └───────────────────────────┘  │  │
                   │  └─────────────────────────────────┘  │
                   │  ┌─────────────────────────────────┐  │
                   │  │   SQLite → PostgreSQL           │  │
                   │  └─────────────────────────────────┘  │
                   │  ┌─────────────────────────────────┐  │
                   │  │   Next.js Web Dashboard         │  │
                   │  └─────────────────────────────────┘  │
                   └───────────────────────────────────────┘
```

---

## Current Status

### ✅ Completed (MVP)

| Component | File | Status |
|-----------|------|--------|
| Decision Engine | `backend/decision_engine.py` | ✅ All 7 rules implemented |
| Mock GSP | `backend/gsp_client.py` | ✅ Test data provider |
| Database | `backend/database.py` | ✅ SQLite audit trail |
| API Server | `backend/server.py` | ✅ FastAPI with CORS |
| Web Dashboard | `frontend/itc-shield/` | ✅ GSTIN check + results |

### ⏳ Pending

| Component | Effort | Cost |
|-----------|--------|------|
| Cloud Deployment | 1 hour | ✅ DONE |

| GSP API Integration | 1-2 days | ₹15,000/year |
| Tally TDL Plugin | 2-3 weeks | ₹40,000-60,000 |
| PDF Certificates | 2-3 hours | ₹0 |
| User Authentication | 3-4 hours | ₹0 |

---

## Decision Rules Implemented

### STOP Rules (Block Payment)
| ID | Condition | Risk | Data Needed |
|----|-----------|------|-------------|
| **S1** | GST Status = Cancelled | CRITICAL | `gst_status` |
| **S2** | GST Status = Suspended | CRITICAL | `gst_status` |
| **S3** | GSTR-3B not filed 2+ months | CRITICAL | `filing_history[]` |

### HOLD Rules (CFO Review)
| ID | Condition | Risk | Data Needed |
|----|-----------|------|-------------|
| **H1** | GSTR-3B filed but delayed 30+ days | HIGH | `filing_date` |
| **H2** | Registration < 6 months old | MEDIUM | `registration_date` |
| **H3** | Legal Name ≠ Trade Name (>30%) | MEDIUM | `legal_name`, `trade_name` |

### RELEASE Rule
| ID | Condition | Risk |
|----|-----------|------|
| **R1** | GST Active + GSTR-3B filed on time | LOW |

---

## Tally TDL Plugin Specification

> **For Freelancer Hiring**

### Compatibility Required
| Version | Market Share | Priority |
|---------|--------------|----------|
| **TallyPrime 7.x** | Growing | 🔴 High |
| **TallyPrime 4.x-6.x** | Large | 🔴 High |
| **Tally ERP 9** | 40%+ market | 🔴 Critical |

### Technical Specification
```
REQUIREMENT: Tally TDL Plugin (ALL VERSIONS)
────────────────────────────────────────────────────

TRIGGER: On Payment Voucher Accept (Ctrl+A)

ACTION:
1. Extract: PartyGSTIN, Amount, PartyName, Date
2. HTTP POST to: https://api.itcshield.in/check
   Content-Type: application/json
3. Parse JSON response

RESPONSE HANDLING:
- "action": "STOP"  → Block save + Red popup
- "action": "HOLD"  → Yellow warning + Allow save  
- "action": "ALLOW" → Silent pass

ERROR HANDLING:
- Network timeout (3s): Fail-open with warning
- Server error: Fail-open with warning
- Invalid response: Fail-open with warning

────────────────────────────────────────────────────
```

**Estimated Cost:** ₹40,000 - ₹60,000

---

## Implementation Phases

### Phase 1: Backend Core ✅ DONE
- [x] Create `gsp_client.py` with mock data
- [x] Update `decision_engine.py` with all 7 rules
- [x] Create `database.py` with SQLite
- [x] Update `server.py` with CORS
- [x] Test all decision rules

### Phase 2: Frontend Dashboard ✅ DONE
- [x] Create Next.js project
- [x] Build GSTIN check form
- [x] Build STOP/HOLD/RELEASE result cards
- [x] Add test scenario buttons

### Phase 3: Cloud Deployment ✅ DONE
- [x] Deploy backend to Render.com
- [x] Configure environment variables (JWT_SECRET, DATABASE_URL)
- [x] Set up Supabase PostgreSQL with Connection Pooler
- [x] Test public URLs


### Phase 4: Tally TDL ⏳ FREELANCER
- [ ] Find TDL developer (Upwork/local)
- [ ] Share specification document
- [ ] Test with cloud API
- [ ] Verify on all Tally versions

### Phase 5: Production ⏳ LATER
- [ ] Buy GSP API subscription
- [ ] Replace mock data with real API
- [ ] Add PDF certificate generation
- [ ] Add user authentication

---

## Budget Summary

| Item | Cost |
|------|------|
| MVP Development | ₹0 (done) |
| Cloud Hosting (1 year) | ₹0 (free tier) |
| **TDL Freelancer** | **₹50,000** |
| GSP API (1 year) | ₹15,000 |
| Domain | ₹500 |
| **Total** | **₹65,500** |

---

## How to Run (Current)

### Backend
```bash
cd backend
pip install -r requirements.txt
python server.py
# Runs at http://localhost:8000
```

### Frontend
```bash
cd frontend/itc-shield
npm install
npm run dev
# Runs at http://localhost:3000
```

---

## Test GSTINs

| GSTIN | Expected Result |
|-------|-----------------|
| `01AABCU9603R1ZX` | 🚫 STOP (Cancelled) |
| `02AABCU9603R1ZX` | 🚫 STOP (Suspended) |
| `03AABCU9603R1ZX` | 🚫 STOP (Non-Filer) |
| `04AABCU9603R1ZX` | ⚠️ HOLD (Late Filer) |
| `05AABCU9603R1ZX` | ⚠️ HOLD (New Vendor) |
| `06AABCU9603R1ZX` | ⚠️ HOLD (Name Mismatch) |
| `33AABCU9603R1ZX` | ✅ RELEASE |
