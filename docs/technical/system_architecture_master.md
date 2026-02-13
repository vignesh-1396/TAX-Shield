# Enterprise SaaS System Design: ITC Protection & Legal Defense Platform

> **Role:** Principal Architect + CTO
> **Document Purpose:** Full Technical System Design (End-to-End)
> **Target:** B2B Enterprise SaaS (India GST Rule 37A Compliance)
> **Status:** Architecture Frozen for Development

---

## 1. Product Context (Immutable)
*Refer to `detailed_product_plan.md` and `decision_logic.md` for functional specs.*

*   **Core Logic:** Pre-payment gatekeeper (STOP/HOLD/RELEASE).
*   **Infrastructure:** Evidence-first legal defense system.
*   **Target User:** CFOs & Audit Teams (Not just AP Clerks).

---

## 2. Technical Architecture Summary

We are building a **Modular Monolith** initially, designed to split into microservices (Auth, Risk, PDF) at Series A scale.

### High-Level Stack
| Layer | Technology | Reason for Choice |
|:---|:---|:---|
| **Frontend** | **Next.js 14+ (React)** | Server-side rendering for speed; Robust BFF capability. |
| **Backend** | **Python (FastAPI)** | Superior for PDF generation (`ReportLab`), Excel processing (`Pandas`), and future AI/ML. |
| **Database** | **PostgreSQL** | Strict relational integrity (ACID) required for financial audit trails. |
| **Queue** | **Celery + Redis** | Handling massive batch uploads and async GSTN API polling. |
| **Agent** | **Tally TDL** | The "Kill Switch" inside the user's ERP. |
| **Infra** | **AWS (Mumbai)** | Data residency compliance (DPDP Act). |

---

## 3. Frontend Architecture

### 3.1 Tech Stack
*   **Framework:** **Next.js** (App Router).
*   **Styling:** **Tailwind CSS** + **Shadcn UI** (Radix Primitives). Professional, accessible, "CFO-ready" aesthetics.
*   **State Management:** **React Query (TanStack Query)**. Critical for managing the 3 states of GST Data: *Loading, Stale, Valid*.
*   **Auth:** **Clerk** or **NextAuth.js**. (Multi-tenant, Organization support out of the box).
*   **PDF Preview:** `react-pdf` for client-side rendering of the generated certificate bytes.

### 3.2 Frontend Modules
1.  **Onboarding Flow:** Organization KYC (PAN/GSTIN), Team Invitations.
2.  **AP Workstation:**
    *   *Batch Upload:* Drag-and-drop Excel (SheetJS for client-side validation).
    *   *Live Risk View:* Row-by-row status (Green/Yellow/Red indicators).
3.  **Finance Manager Cockpit:**
    *   *Hold Queue:* Dispute resolution interface.
    *   *Release Approval:* Bulk action for "Yellow" flagged vendors.
4.  **CFO Control Tower:**
    *   *Override Workflow:* "Break Glass" UI with mandatory reason logging.
    *   *Audit Trail Viewer:* Read-only view of past decisions.

### 3.3 Frontend Folder Structure
```bash
/frontend
  /app
    /(auth)                  # Login, SSO, OTP
    /(dashboard)             # Authenticated Routes
      /upload                # Payment Batch Processing
      /vendors/[gstin]       # Vendor Risk Profile (360 View)
      /approvals             # Exception Queue
      /audit-logs            # "Time Machine" View
      /settings              # Rules config, User Mgmt
  /components
    /ui                      # Shadcn (Button, Card, Badge)
    /business                # (BatchTable, RiskBadge, OverrideModal)
  /lib
    /api                     # Typed API Client (Axios/Ky)
    /hooks                   # useVendorStatus, useBatchProgress
    /validators              # Zod schemas (matches Backend)
```

---

## 4. Backend Architecture

### 4.1 Backend Stack
*   **Language:** **Python 3.11+**
*   **Framework:** **FastAPI**. High performance, native async support for I/O bound GSTN calls.
*   **API Style:** REST (OpenAPI 3.1 auto-generated docs).
*   **PDF Engine:** **ReportLab** (Pixel-perfect legal documents). *Note: Chosen over HTML-to-PDF because we need exact control for digital signing.*

### 4.2 Core Services (Modular Monolith)

**1. `AuthService`:**
*   Handles JWT validation from Frontend.
*   Enforces RBAC (Scopes: `procurement:read`, `finance:approve`, `admin:all`).

**2. `VendorIntelligenceService` (The Brain):**
*   Implements the **Data Availability Cascade** (Primary GSP -> Backup -> Cache -> NIC).
*   Standardizes status: `Active`, `sluggish_filer`, `potential_37a_risk`.

**3. `RuleEngineService`:**
*   Input: `VendorProfile` + `InvoiceDetails`.
*   Logic: Applies S1-S3 (Stop), H1-H3 (Hold) rules.
*   Output: `DecisionResult` (Status + Human Readable Reason).

**4. `CertificateAuthorityService`:**
*   Generates the "Bona Fide" PDF.
*   Hashes the content (SHA-256).
*   Uploads to S3 WORM (Write Once Read Many) bucket.

**5. `AuditLoggerService`:**
*   Async listener. Writes every API request/response to the `audit_event_log` table.

### 4.3 Sync vs Async
*   **Sync:** Single Vendor Check (from Tally), Login, Dashboard Reads.
*   **Async (Celery):** Batch Excel Uploads (500+ rows), PDF Generation, "Nightly Sweep" of vendor status.

---

## 5. Database & Data Model

### 5.1 Strategy
*   **Database:** **PostgreSQL 16** (Managed RDS).
*   **Caching:** **Redis**.
    *   *Key:* `gstin_status:{gstin}`.
    *   *TTL:* 24 hours (Strict Freshness Policy).

### 5.2 Core Schema

**`organizations`**
*   `id` (UUID), `legal_name`, `pan`, `subscription_tier`

**`vendors`**
*   `gstin` (PK, varchar 15), `trade_name`, `risk_score` (0-100), `last_synced_at`

**`vendor_snapshots` (The "Time Machine")**
*   *Purpose:* Store the EXACT state of a vendor at the moment of check.
*   `id`, `vendor_gstin`, `gst_status` (Active/Cancelled), `filing_history_json`, `created_at`
*   *Index:* `(vendor_gstin, created_at)`

**`payment_batches`**
*   `id`, `org_id`, `uploaded_by`, `status` (Processing, Ready, Failed)

**`compliance_checks`**
*   `id` (UUID), `batch_id`, `vendor_gstin`, `amount`, `decision` (STOP/HOLD/RELEASE), `certificate_url`

**`overrides`**
*   `check_id` (FK), `user_id`, `reason_code`, `justification_text`, `ip_address`

---

## 6. Integration Pipeline

### 6.1 GST Data Pipeline
*   **Source:** Authorized GSPs (Masters India / Vayana).
*   **Resiliency:** Circuit Breaker pattern. If GSP errors > 5%, switch to Backup GSP.
*   **Fallback:** If all APIs down, check local DB cache (valid for 24h). If older, return `HOLD` (Reason: "Verification Unavailable").

### 6.2 Excel Import Pipeline
1.  **Frontend:** Parse Excel -> Validate Columns -> Array of JSON.
2.  **API:** Receive JSON -> Enqueue `ProcessBatchJob`.
3.  **Worker:**
    *   Dedup GSTINs.
    *   Parallel fetch GST Status (Batch API).
    *   Run Rule Engine.
    *   Update DB.
    *   Notify Frontend via WebSocket/Polling.

### 6.3 Tally Integration (The "Kill Switch")
*   **Technology:** TDL (Tally Definition Language) Plugin.
*   **Hook:** `On:FormAccept` (Payment Voucher).
*   **Flow:** Tally -> HTTPS Post -> API -> Decision -> Tally (Block/Allow).
*   *Constraint:* 3-second timeout. If timeout, `Fail Open` with warning.

---

## 7. Exception Flow Handling

| Scenario | System Action | Liability Cover |
|:---|:---|:---|
| **Post-Payment Default** | Automation "Sweep" detects status change 30 days later. Alerts Finance. | Evidence of "Clean Status" on Payment Date is preserved. |
| **CFO Override** | CFO enters reason -> System re-issues Certificate with "OVERRIDDEN" watermark. | Audit trail shifts liability to CFO logic. |
| **Stale Data** | System returns `HOLD`. User can "Force Release" if they have offline proof (Screenhot). | Screenshot is uploaded and linked to Transaction ID. |
| **Dispute** | Vendor claims they filed. System allows "Refetch" button to bypass cache. | Timestamp update proves re-verification. |

---

## 8. Security, Compliance & Trust

### 8.1 Security
*   **Encryption:** AES-256 for DB encryption at rest. TLS 1.3 for all APIs.
*   **Secrets:** Managed via AWS Secrets Manager (GSP Keys, DB Passwords).
*   **Role Separation:** "Maker" (AP Clerk) cannot Approve overrides. "Checker" (CFO) cannot upload batches.

### 8.2 Audit Readiness
*   **Immutable Logs:** `audit_event_log` table is Append-Only.
*   **Digital Signatures:** Future phase - Sign PDFs with DSC token.
*   **Retention:** 8 Years (Income Tax Act alignment).

### 8.3 Compliance
*   **Residency:** AWS `ap-south-1` (Mumbai).
*   **Disclaimer:** "Decision Support Tool". We process public data; we do not certify tax compliance.

---

## 9. Infrastructure & Deployment

### 9.1 Cloud Architecture (AWS)
*   **Compute:** AWS Fargate (Serverless Containers) for API.
*   **Database:** Amazon RDS (Postgres).
*   **Storage:** Amazon S3 (Private Buckets) for Certificates.
*   **CDN:** CloudFront for Frontend assets.

### 9.2 CI/CD Pipeline (GitHub Actions)
1.  **Commit:** Lint (Ruff), Type Check (MyPy).
2.  **Test:** PyTest (Unit + Integration with Mock GSP).
3.  **Build:** Dockerize -> ECR.
4.  **Deploy:** Terraform applies changes to ECS Service.
5.  **Rollback:** Automatic if Health Check fails.

### 9.3 Observability
*   **Logging:** Structlog (JSON logs) -> CloudWatch / Datadog.
*   **Alerts:** "GSP Error Rate > 5%", "Tally Latency > 2s".

---

## 10. Phase-Wise Roadmap

### Phase 0: MVP (The "Gatekeeper")
*   **Goal:** Single User, Excel Upload, Basic Risk Check.
*   **Tech:** Next.js + FastAPI + Mock GSP.
*   **Feature:** Validation of "Active/Cancelled" status.
*   **Deliverable:** PDF Certificate Download.

### Phase 1: Protection Layer
*   **Goal:** Multi-user, History, Tally Plugin.
*   **Tech:** RDS Integration, TDL "Kill Switch".
*   **Feature:** "Time Machine" Logic, Rule 37A (3-month check).

### Phase 2: Defense Layer
*   **Goal:** CFO Workflow.
*   **Tech:** "Override" UIs, Audit Logging.
*   **Feature:** Notice Management (Upload Notice -> Find Payment).

### Phase 3: Control Layer (Enterprise)
*   **Goal:** Full Automation.
*   **Tech:** Bank Integration (H2H or File Gen).
*   **Feature:** "Nightly Sweep" of all 5000+ vendors.
