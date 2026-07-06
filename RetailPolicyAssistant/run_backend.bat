@echo off
REM This script properly activates the venv and runs the backend

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/Updating uuid-utils in venv...
python -m pip install uuid-utils --quiet

echo.
echo Starting backend on port 8001...
python -m uvicorn app.main:app --reload --port 8001

pause
