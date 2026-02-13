# Windows Setup Guide

## Prerequisites
Before you copy this folder to your Windows machine, ensure you have:
1.  **Python 3.11+** installed (Check with `python --version`).
2.  **Node.js (LTS)** installed (Check with `node -v`).
3.  **Git** (Optional, but recommended).

## Steps to Run

### 1. Copy the Folder
Copy the entire `ITC_Protection_System` folder to your Windows Desktop or Documents.

### 2. Environment Variables
**Crucial Step:**
- Go to `backend/` folder.
- Create a file named `.env` (if it doesn't exist).
- Add your Supabase keys (you can copy these from the Mac `.env` file):
  ```ini
  DATABASE_URL=...
  SUPABASE_URL=...
  SUPABASE_SERVICE_KEY=...
  SUPABASE_ANON_KEY=...
  GSP_ENVIRONMENT=...
  GSP_CLIENT_ID=...
  GSP_CLIENT_SECRET=...
  ```
*Note: Do not commit `.env` to Git/GitHub for security.*

### 3. One-Click Start
- Double-click `start_win.bat`.
- It will automatically:
    - Create a Python virtual environment (`venv_win`).
    - Install backend dependencies (`pip install ...`).
    - Install frontend dependencies (`npm install ...`).
    - Launch both servers.

### 4. Access the App
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

## Troubleshooting
*   **"Python not found"**: Make sure Python is added to your System PATH during installation.
*   **"npm is not recognized"**: Reinstall Node.js and restart your computer.
*   **Database Error**: Check if your IP address is allowed in Supabase (if you have IP restrictions enabled).
