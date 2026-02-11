@echo off
TITLE ITC Protection System - Launcher

echo ==========================================
echo   ITC Protection System - Portable Mode
echo ==========================================

:: 1. Backend Setup
echo.
echo [1/2] Setting up Backend...
cd backend
IF NOT EXIST "venv_win" (
    echo Creating virtual environment...
    python -m venv venv_win
)
call venv_win\Scripts\activate
echo Installing dependencies...
pip install -r requirements.txt

:: Start Backend in new window
echo Starting Backend Server...
start "ITC Backend (Port 8000)" cmd /k "venv_win\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"

:: 2. Frontend Setup
echo.
echo [2/2] Setting up Frontend...
cd ..\frontend\itc-shield
IF NOT EXIST "node_modules" (
    echo Installing node modules (this may take a while)...
    call npm install
)

:: Start Frontend in new window
echo Starting Frontend Dashboard...
start "ITC Dashboard (Port 3000)" cmd /k "npm run dev"

echo.
echo ==========================================
echo   Succcess! System is starting up.
echo   - Backend: http://localhost:8000
echo   - Frontend: http://localhost:3000
echo.
echo   Keep this window open or close to exit.
echo ==========================================
pause
