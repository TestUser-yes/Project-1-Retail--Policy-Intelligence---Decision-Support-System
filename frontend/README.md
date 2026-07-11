# Retail Policy Intelligence - Frontend

Modern React-based frontend for the Retail Policy Intelligence & Decision Support System.

## Architecture

```
frontend/
├── src/
│   ├── api/              # API client and endpoint definitions
│   ├── components/       # Reusable React components
│   ├── context/          # React Context for state management
│   ├── hooks/            # Custom React hooks
│   ├── pages/            # Page components (routes)
│   ├── types/            # TypeScript type definitions
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── index.html            # HTML template
├── vite.config.ts        # Vite configuration
├── tsconfig.json         # TypeScript configuration
├── package.json          # Dependencies
└── .env.development      # Environment variables
```

## Tech Stack

- **Framework**: React 18.3.1
- **Build Tool**: Vite 5.2.11
- **Language**: TypeScript 5.4.5
- **UI Library**: React Bootstrap 2.10.2
- **HTTP Client**: Axios 1.7.2
- **Routing**: React Router 6.23.2
- **State Management**: React Context API

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment file:
```bash
cp .env.example .env.development
```

4. Update `.env.development` with your backend URL (if not localhost:8001)

## Development

Start the development server:
```bash
npm run dev
```

The application will open at `http://localhost:3000` with hot module reloading.

### Development features
- Fast refresh enabled
- API proxy configured to `http://localhost:8001`
- TypeScript type checking
- ESLint configured

## Building

Create a production build:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Project Structure

### API Layer (`src/api/`)
- **client.ts**: Axios instance with interceptors and error handling
- **auth.ts**: Authentication endpoints (login, logout, status, refresh)
- **query.ts**: Query/conversation endpoints
- **dashboard.ts**: Dashboard and observability endpoints
- **documents.ts**: Document upload and management endpoints

### State Management (`src/context/`)
- **AuthContext.tsx**: Authentication state and user management

### Custom Hooks (`src/hooks/`)
- **useNotification.ts**: Toast notifications and alerts

### Components (`src/components/`)
- **Layout.tsx**: Main layout with sidebar and navbar
- **KPICard.tsx**: Key performance indicator card component
- **LoadingSpinner.tsx**: Loading state component
- **ErrorAlert.tsx**: Error message component
- **Toast.tsx**: Toast notification component
- **ToastContainer.tsx**: Toast container for multiple notifications
- **ProtectedRoute.tsx**: Route guard for authentication

### Pages (`src/pages/`)
- **Login.tsx**: Authentication page with demo credentials
- **Dashboard.tsx**: Main dashboard with KPIs and metrics
- **Assistant.tsx**: AI assistant chat interface
- **Documents.tsx**: Document upload and management
- **Admin.tsx**: Admin panel (role-restricted)

### Types (`src/types/`)
- Complete TypeScript interfaces for all API models
- Authentication types
- Query and response types
- Dashboard types
- Error types

## Authentication Flow

1. User visits `/login`
2. Clicks "Login as Demo User"
3. Frontend calls `POST /token` to get access/refresh tokens
4. Tokens stored in secure httpOnly cookies (backend-managed)
5. Frontend redirects to dashboard
6. Protected routes check authentication via `useAuth()` hook
7. API requests automatically include cookies or Bearer tokens
8. On 401 response, automatic token refresh attempts
9. Logout clears cookies and redirects to login

## API Integration

All API calls are made through the centralized `apiClient`:

```typescript
import apiClient from '@/api/client'

// Usage
const data = await apiClient.get('/endpoint')
const response = await apiClient.post('/endpoint', data)
```

### Error Handling
- 401 Unauthorized: Attempts token refresh, then redirects to login
- 4xx Client Errors: Passed to component for user feedback
- 5xx Server Errors: Logged and displayed as alerts

### Authentication
- Credentials automatically included (httpOnly cookies)
- Bearer token support for API clients
- Automatic token refresh on expiration

## Features

### Dashboard
- Real-time KPI metrics
- Query history table
- System health status
- Document statistics
- Vendor information
- Auto-refresh every 30 seconds

### AI Assistant
- Real-time chat interface
- Multi-turn conversations
- Query confidence scores
- Cost tracking per query
- Source citations from documents
- Latency metrics
- Risk assessment display
- Response details panel

### Document Management
- PDF upload with progress tracking
- Document list with metadata
- Delete documents
- File validation (PDF only)
- Size and chunk information
- Indexed timestamp tracking

### Admin Panel
- Role-based access control
- Admin-only routes
- Extensible for future features

## Styling

Bootstrap 5 is used as the base styling framework with custom CSS for:
- Sidebar navigation
- Chat interface
- KPI cards
- Toast notifications
- Responsive layouts

All custom styles are in `src/index.css`

## Environment Variables

```bash
VITE_API_URL=http://localhost:8001          # Backend API URL
VITE_APP_NAME=Retail Policy Intelligence    # App name
VITE_APP_VERSION=1.0.0                      # Version
```

## Performance Optimization

- Code splitting via Vite
- Tree-shaking of unused code
- Minification in production
- Image optimization ready
- Lazy route loading capable
- Memoization of expensive components

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development Commands

```bash
npm run dev          # Start dev server
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

## Backend API Contract

The frontend consumes these backend endpoints:

### Authentication
- `POST /token` - Get access/refresh tokens
- `GET /auth/status` - Check authentication status
- `POST /token/refresh` - Refresh access token
- `POST /logout` - Logout and clear tokens

### Queries
- `POST /ask` - Ask policy question with routing
- `GET /conversations/{id}/history` - Get conversation history

### Dashboard
- `GET /api/dashboard` - Get dashboard metrics
- `GET /api/observability` - Get system observability data
- `GET /health` - Check backend health

### Documents
- `POST /api/ingestion/ingest` - Upload PDF document
- `GET /api/ingestion/retrieve` - List documents
- `DELETE /api/ingestion/delete/{filename}` - Delete document

Full API contract: See `../API_CONTRACT_COMPLETE.md`

## Troubleshooting

### Blank page on startup
- Check browser console for errors
- Verify backend is running on correct port
- Check `.env.development` has correct `VITE_API_URL`

### Authentication errors
- Ensure backend is accessible
- Check cookies are enabled in browser
- Verify token endpoint returns correct response

### API requests failing
- Check CORS configuration in backend
- Verify API endpoint paths match backend routes
- Check network tab in browser DevTools

### Build errors
- Run `npm install` to ensure all dependencies
- Clear `node_modules` and reinstall if issues persist
- Check TypeScript errors: `npm run type-check`

## Future Enhancements

- WebSocket support for real-time updates
- Advanced analytics visualizations
- Query templates and saved searches
- User preferences and customization
- Role-based UI customization
- Offline support with service workers
- Mobile app (React Native)
- Advanced filtering on dashboard
- Export/import conversations
- Multi-language support

## Contributing

1. Ensure code follows ESLint rules
2. Add TypeScript types for new features
3. Test new components with different states
4. Update this README for new features
5. Follow the existing code structure

## License

Proprietary - Retail Policy Intelligence System
