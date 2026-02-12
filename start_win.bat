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
:: Ensure pip is up to date
python -m pip install --upgrade pip
:: Install all requirements including python-dotenv
pip install -r requirements.txt
pip install python-dotenv

:: Check for .env file
IF NOT EXIST ".env" (
    echo WARNING: .env file missing in backend folder!
    echo Creating a template .env file...
    type nul > .env
    echo SUPABASE_URL=YOUR_SUPABASE_URL_HERE>> .env
    echo SUPABASE_KEY=YOUR_SUPABASE_KEY_HERE>> .env
    echo Please edit backend/.env with your actual keys.
    pause
)

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
