# Developer Handover Guide: ITC Shield

This document provides a technical overview of the **ITC Shield** project, its current SaaS-ready architecture, and the roadmap for completion.

## 🏗️ Project Architecture

The project has been restructured following modern SaaS best practices (Tiered Architecture).

### 1. Backend (FastAPI)
Located in `/backend`. Uses a modular structure:
- **`app/main.py`**: Entry point and middleware configuration.
- **`app/api/v1/`**: Versioned API routers (Auth, Compliance, Batch, Tally).
- **`app/core/`**: Global configuration (Pydantic Settings) and security utilities (JWT, Hashing).
- **`app/db/`**: 
    - `session.py`: Handles dual-database support (PostgreSQL for Prod, SQLite for Dev).
    - `crud/`: Isolated database logic for `vendors`, `checks`, `batch_jobs`, and `users`.
- **`app/services/`**: Business logic, including the `DecisionEngine`, `MockGSPProvider`, and `PDFGenerator`.
- **`app/schemas/`**: Pydantic models for request/response validation.

### 2. Frontend (Next.js)
Located in `/frontend/itc-shield`. Organized under `src/`:
- **`src/app/`**: Application routes using the Next.js App Router.
- **`src/context/`**: Global state (e.g., `AuthContext` for JWT handling).
- **`src/components/`**: UI components (layouts, shared elements).

## 🚀 Local Setup

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. `pip install -r requirements.txt`
5. Create a `.env` file based on the config in `app/core/config.py`.
6. Run: `uvicorn app.main:app --reload`

### Frontend
1. `cd frontend/itc-shield`
2. `npm install`
3. `npm run dev`
4. Access at `http://localhost:3000`.

## 🛠️ Key Services to Implement
- **Real GSP Integration**: Replace `app/services/gsp.py` with actual API calls to a provider (e.g., Masters India).
- **Multi-Tenancy**: The DB schema and CRUD operations are prepared for `user_id/company_id` filtering.
- **Production Postgres**: Use the `DATABASE_URL` env var to point to a production PostgreSQL instance.

## 📦 Deployment
- **Backend**: Configured for **Render.com** (see `render.yaml`).
- **Frontend**: Recommended for **Vercel**.
- **Database**: Recommended to use **Supabase** or **Render Postgres**.
