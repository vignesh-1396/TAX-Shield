# 📋 Phase 2 Task List: GSTR-2B Implementation

## 🏗️ 2.1 Database Setup (Current)
- [x] Create `gst_credentials` table (Stores User's GST session/tokens)
- [x] Create `gstr_2b_data` table (Stores GSTR-2B invoices)
- [x] Create `otp_logs` table (Optional: For audit, though we don't store OTPs)
- [x] Verify migration on active database (SQLite/Postgres)

## 🔌 2.2 API Integration (GSP Sandbox)
- [ ] Implement `GSPClient` v2 methods:
    - [ ] `request_otp(username)`
    - [ ] `verify_otp(otp, txn_id)` -> returns `auth_token`
    - [ ] `fetch_gstr2b(return_period, token)`
- [ ] Create Backend API Endpoints:
    - [ ] `POST /api/v1/gst/connect` (Initiate OTP)
    - [ ] `POST /api/v1/gst/verify` (Submit OTP)
    - [ ] `GET /api/v1/gst/status` (Check if connected)

## 🤖 2.3 Reconciliation Engine
- [ ] Update `DecisionEngine` to check `gstr_2b_data` table
- [ ] Implement Matching Logic:
    - [ ] Exact Match (Invoice No + Date)
    - [ ] Fuzzy Match (Invoice No cleanup)
    - [ ] Tax Amount Tolerance (± ₹5)
- [ ] Implement Rule 37 Logic (180 Days check)

## 🖥️ 2.4 Frontend (React)
- [ ] Create `ConnectGST` Component (Settings Page)
- [ ] Create OTP Input Dialog
- [ ] Show "Connection Status" in Dashboard
- [ ] Allow manual "Sync Now" trigger

## 🧪 2.5 Testing
- [ ] Unit Test: Reconciliation Logic
- [ ] Integration Test: Mock GSP Responses
- [ ] User Acceptance Test: Connect GSTIN Flow
