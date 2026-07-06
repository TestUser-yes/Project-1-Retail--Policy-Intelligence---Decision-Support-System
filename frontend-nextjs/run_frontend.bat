@echo off
REM This script runs the frontend on port 3000

cd /d "%~dp0"

echo Starting frontend on port 3000...
npm run dev

pause
