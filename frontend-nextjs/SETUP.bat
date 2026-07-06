@echo off
echo.
echo 🚀 Setting up Retail Policy Intelligence - Next.js Frontend
echo ===========================================================
echo.

:: Check Node.js
echo 📦 Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install from https://nodejs.org
    exit /b 1
)

echo ✅ Found:
node --version
echo.

:: Install dependencies
echo 📥 Installing dependencies...
call npm install

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

echo ✅ Dependencies installed
echo.

:: Create .env.local
if not exist .env.local (
    echo 📝 Creating .env.local...
    (
        echo NEXT_PUBLIC_API_URL=http://localhost:8001
    ) > .env.local
    echo ✅ Created .env.local
)

echo.
echo ===========================================================
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Make sure backend is running on http://localhost:8001
echo 2. Run: npm run dev
echo 3. Open: http://localhost:3000
echo.
echo For production build: npm run build ^&^& npm start
pause
