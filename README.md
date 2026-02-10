# ITC Shield - GST Vendor Compliance System

> **Protect your business from ITC reversals** - Real-time GST compliance checking integrated with Tally

![Status](https://img.shields.io/badge/Status-MVP%20Ready-green)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)

---

## 🎯 What It Does

TaxPayGuard is a comprehensive vendor due diligence and compliance system designed to protect businesses' Input Tax Credit (ITC). It verifies GST filing status (specifically Rule 37A compliance) and generates professional due diligence certificates.

| Scenario | Without TaxPayGuard | With TaxPayGuard |
|----------|-------------------|-----------------|
| Pay vendor with cancelled GST | ❌ ITC Reversed (18% loss) | ✅ Payment blocked |
| Pay non-filing vendor | ❌ Rule 37A violation | ✅ Warning shown |
| Compliant vendor | ✅ OK | ✅ Certificate generated |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   TALLY         │────▶│   ITC SHIELD    │────▶│   GSP API       │
│   (TDL Plugin)  │     │   (FastAPI)     │     │   (GST Data)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                        ┌──────┴──────┐
                        │  Dashboard  │
                        │  (Next.js)  │
                        └─────────────┘
```

---

## 📁 Project Structure

```
ITC_Protection_System/
├── backend/                 # Python FastAPI Server
│   ├── server.py           # Main API endpoints
│   ├── decision_engine.py  # 7 compliance rules (S1-S3, H1-H3, R1)
│   ├── gsp_client.py       # GSP API client (mock for now)
│   ├── database.py         # SQLite audit trail
│   └── certificate_gen.py  # PDF generator
│
├── frontend/               # Next.js Dashboard
│   └── itc-shield/
│       └── app/
│           ├── page.js     # Main UI
│           └── globals.css # Styling
│
├── tally/                  # Tally Integration
│   └── itc_shield.tdl      # TDL plugin (needs freelancer)
│
└── docs/                   # Documentation
    ├── technical/          # System architecture, decision logic
    ├── business/           # Commercial strategy, pricing
    ├── product/            # Product roadmap
    └── go_to_market/       # Sales strategy
```

---

## 🚀 Quick Start

### 1. Start Backend
```bash
cd backend
pip install fastapi uvicorn pydantic
python server.py
```
API runs at: http://localhost:8000

### 2. Start Frontend
```bash
cd frontend/itc-shield
npm install
npm run dev
```
Dashboard at: http://localhost:3000

### 3. Test It
Open http://localhost:3000 and click any test scenario.

---

## 📋 Decision Rules

| Rule | Condition | Decision |
|------|-----------|----------|
| **S1** | GST Status = Cancelled | 🚫 STOP |
| **S2** | GST Status = Suspended | 🚫 STOP |
| **S3** | GSTR-3B not filed 2+ months | 🚫 STOP |
| **H1** | Filing delayed 30+ days | ⚠️ HOLD |
| **H2** | Registration < 6 months | ⚠️ HOLD |
| **H3** | Name mismatch > 30% | ⚠️ HOLD |
| **R1** | All compliant | ✅ RELEASE |

---

## 🧪 Test GSTINs

| GSTIN | Expected Result |
|-------|-----------------|
| `01AABCU9603R1ZX` | STOP (Cancelled) |
| `02AABCU9603R1ZX` | STOP (Suspended) |
| `03AABCU9603R1ZX` | STOP (Non-Filer) |
| `04AABCU9603R1ZX` | HOLD (Late) |
| `05AABCU9603R1ZX` | HOLD (New) |
| `06AABCU9603R1ZX` | HOLD (Name Mismatch) |
| `33AABCU9603R1ZX` | RELEASE |

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/check_compliance` | Check single vendor |
| GET | `/vendor/{gstin}` | Get vendor details |
| GET | `/history` | Audit trail |
| GET | `/docs` | Swagger documentation |

---

## 📈 Roadmap

- [x] Decision Engine (7 rules)
- [x] Web Dashboard
- [x] SQLite Database
- [ ] Cloud Deployment (Render.com)
- [ ] Real GSP API Integration
- [ ] Tally TDL Plugin (Freelancer)
- [ ] PDF Certificates
- [ ] User Authentication

---

## 📄 License

Proprietary - All Rights Reserved
