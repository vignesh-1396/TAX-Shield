# TaxPay Guard - Tally TDL Installation Guide

## Quick Start

### Step 1: Download TDL File
Copy `TaxPayGuard.TDL` from this folder to your Tally installation.

### Step 2: Locate Tally TDL Folder

| Tally Version | TDL Location |
|---------------|--------------|
| **Tally Prime** | `C:\Users\[Username]\AppData\Local\TallyPrime\TDL` |
| **Tally ERP 9** | `C:\Tally.ERP9\` (same folder as Tally.exe) |

### Step 3: Configure Tally
1. Open Tally
2. Press `F12` → Configuration → TDL Configuration
3. Enable `TaxPayGuard.TDL`
4. Press `Esc` to save

### Step 4: Configure API URL
Edit the TDL file and change this line to your server URL:
```
TPG API URL : "http://localhost:8000/tally/check"
```

For cloud deployment, use:
```
TPG API URL : "https://api.taxpayguard.in/tally/check"
```

---

## How It Works

```
┌─────────────┐      ┌─────────────────┐      ┌───────────────┐
│   Tally     │ ──→  │ TaxPay Guard    │ ──→  │   Decision    │
│   Payment   │      │     API         │      │   S1-S3/H1-H3 │
└─────────────┘      └─────────────────┘      └───────────────┘
       │                    │                        │
       └────────────────────┴────────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
              Block Save         Allow Save
             (STOP popup)     (HOLD warn / RELEASE)
```

---

## Decision Logic

| Decision | Tally Behavior |
|----------|----------------|
| **🚫 STOP** | Blocks payment save, shows error |
| **⚠️ HOLD** | Shows warning, asks for confirmation |
| **✅ RELEASE** | Allows save silently |

---

## Test Scenarios

| GSTIN | Expected Result |
|-------|-----------------|
| `01AABCU9603R1ZX` | 🚫 STOP (Cancelled) |
| `04AABCU9603R1ZX` | ⚠️ HOLD (Late Filer) |
| `33AABCU9603R1ZX` | ✅ RELEASE (Compliant) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| TDL not loading | Check file path, restart Tally |
| API connection error | Verify server is running, check firewall |
| "No GSTIN found" | Add GSTIN to vendor ledger master |

---

## Support
Contact: support@taxpayguard.in
