@echo off
REM Frontend startup script for Retail Policy Intelligence System
REM Handles the special characters in the path

cd frontend
echo Starting Vite development server...
echo.
echo Frontend will be available at: http://localhost:5173
echo.

REM Run vite directly from node_modules
call npx vite

pause
