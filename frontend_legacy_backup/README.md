# Retail Policy Intelligence - Next.js Frontend

Production-grade Next.js frontend for the Retail Policy Intelligence system.

## Features

✅ Out-of-Scope Query Detection
✅ SLO Metrics Tracking & Display
✅ Escalation & Handoff Workflow
✅ Beautiful Tailwind CSS UI
✅ TypeScript for type safety
✅ Real-time API integration

## Getting Started

```bash
npm install
npm run dev
```

Visit `http://localhost:3000`

## Backend Requirements

Make sure FastAPI backend is running on `http://localhost:8000`

```bash
cd RetailPolicyAssistant
uvicorn app.main:app --reload
```

## Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
app/
  ├── components/       # React components
  ├── lib/              # API client & utilities
  ├── page.tsx          # Home page
  ├── layout.tsx        # Root layout
  ├── globals.css       # Global styles
  └── query/
      └── page.tsx      # Query page
```

## Features Explained

### 1. Out-of-Scope Detection
Automatically detects queries unrelated to retail policies/vendors and escalates them.

### 2. SLO Metrics
Tracks latency against 2-second target:
- Green: ≤ 2000ms (pass)
- Yellow: 1600-2000ms (warning)
- Red: > 2000ms (fail)

### 3. Escalation & Handoff
Beautiful modal for routing queries to compliance officers with audit trail.

## Environment Variables

```
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend URL
```

## Technologies

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP client
