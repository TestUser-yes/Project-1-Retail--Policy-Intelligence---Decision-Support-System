#!/bin/bash
# Frontend Setup Script - Creates beautiful React frontend for capstone

set -e

echo "=================================================="
echo "  Retail Policy Intelligence - React Frontend"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "RetailPolicyAssistant/app/main.py" ]; then
    echo "Error: Please run this from the project root directory"
    exit 1
fi

# Create React project
echo "📦 Creating React frontend..."
npm create vite@latest frontend -- --template react
cd frontend

echo "📥 Installing dependencies..."
npm install
npm install axios react-router-dom @tanstack/react-query
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

echo ""
echo "✅ Frontend project created successfully!"
echo ""
echo "Next steps:"
echo "1. Copy components and services to frontend/src/"
echo "2. Configure .env.local with API URL"
echo "3. Run: npm run dev"
echo ""
