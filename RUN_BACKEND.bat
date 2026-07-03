@echo off
REM Backend startup script for Retail Policy Intelligence System
REM Handles the special characters in the path

cd RetailPolicyAssistant
echo Starting FastAPI backend server...
echo.
echo Backend will be available at: http://localhost:8000
echo API Health Check: http://localhost:8000/health
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --port 8000

pause
