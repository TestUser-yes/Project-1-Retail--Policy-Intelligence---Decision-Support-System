#!/bin/bash

echo "🚀 Setting up Retail Policy Intelligence - Next.js Frontend"
echo "=========================================================="
echo ""

# Check Node.js
echo "📦 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✅ Found $NODE_VERSION"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    echo "✅ Created .env.local"
fi

echo ""
echo "=========================================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure backend is running on http://localhost:8000"
echo "2. Run: npm run dev"
echo "3. Open: http://localhost:3000"
echo ""
echo "For production build: npm run build && npm start"
