# Sentinel Frontend

This is the frontend application for the Sentinel cybersecurity monitoring platform, built with [Next.js](https://nextjs.org) and TypeScript.

## Overview

The Sentinel frontend provides a web interface for security monitoring, investigation, and system administration. It connects to the Sentinel backend API for data retrieval and authentication.

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm, yarn, or pnpm
- Sentinel backend running (default: http://localhost:8000)

### Installation

```bash
npm install
# or
yarn install
# or
pnpm install
```

### Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_APP_NAME=Sentinel
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DEBUG_MODE=true
```

### Development

Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

### Testing

Run the test suite:

```bash
npm test
# or
yarn test
# or
pnpm test
```

Run tests in watch mode:

```bash
npm run test:watch
# or
yarn test:watch
# or
pnpm test:watch
```

Run tests with coverage:

```bash
npm run test:coverage
# or
yarn test:coverage
# or
pnpm test:coverage
```

### Build

Build the production application:

```bash
npm run build
# or
yarn build
# or
pnpm build
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── dashboard/         # Dashboard page
│   │   ├── findings/           # Findings management
│   │   ├── events/             # Event viewing
│   │   ├── detections/         # Detection rules
│   │   ├── health/             # System health
│   │   ├── login/              # Authentication
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Homepage
│   ├── components/            # React components
│   │   ├── common/             # Shared UI components
│   │   ├── dashboard/         # Dashboard-specific components
│   │   ├── findings/           # Finding-related components
│   │   ├── events/             # Event-related components
│   │   ├── detections/         # Detection rule components
│   │   └── health/             # Health monitoring components
│   ├── lib/                   # Utility libraries
│   │   ├── api/                # API client layer
│   │   ├── auth/               # Authentication utilities
│   │   ├── validation/         # Form validation
│   │   ├── safe-rendering/     # Safe content rendering utilities
│   │   └── index.ts            # Central library exports
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript type definitions
│   └── tests/                 # Frontend tests
├── public/                    # Static assets
├── jest.config.ts             # Jest configuration
├── jest.setup.js              # Jest setup
├── next.config.ts             # Next.js configuration
├── tailwind.config.ts         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── package.json              # Dependencies and scripts
```

## Key Features

- **TypeScript**: Full type safety across the application
- **Next.js App Router**: Modern React framework with server components
- **Tailwind CSS**: Utility-first CSS framework
- **Centralized API Client**: Single API communication layer
- **Authentication**: JWT-based authentication with permission checks
- **Modular Architecture**: Clear separation of concerns
- **Testing**: Comprehensive test coverage with Jest
- **Security Dashboard**: Real-time security monitoring overview

## Dashboard

The Sentinel security dashboard provides analysts with a high-level view of the current security state.

### Dashboard Features

**Severity Metrics:**
- Critical, High, Medium, Low severity breakdown
- Total findings count
- Color-coded severity indicators with icons
- Loading states with skeleton loaders
- Accessibility-friendly (color + icon dual indication)

**Recent Findings:**
- List of recent security findings
- Severity and status badges
- Links to investigation views
- Configurable max items display
- Loading, error, and empty states
- "View all findings" link when truncated

**System Health:**
- API status monitoring
- Database status monitoring
- Detection engine status monitoring
- Three status levels: Healthy, Degraded, Unavailable
- Last check timestamps
- Status indicators with color + icon dual indication

**Data Refresh:**
- Manual refresh button
- Last refresh timestamp display
- Optional auto-refresh (30-second intervals)
- Loading state indication
- Keyboard shortcut support (Ctrl/Cmd + R)

**Keyboard Navigation:**
- Ctrl/Cmd + R: Refresh dashboard
- Alt + F: Navigate to findings
- Alt + E: Navigate to events
- Alt + D: Navigate to detections
- Alt + H: Navigate to health

### Dashboard Components

The dashboard is built from modular components:

- `MetricsCard`: Reusable metric display card
- `SeverityMetrics`: Severity breakdown component
- `RecentFindings`: Recent findings list with links
- `RecentDetections`: Recent detection activity (placeholder)
- `SystemHealth`: Component health monitoring
- `DashboardRefresh`: Data refresh controls
- `DashboardKeyboardNav`: Keyboard navigation (invisible)

### Dashboard Accessibility

The dashboard follows accessibility best practices:

- Semantic HTML structure
- ARIA labels for all interactive elements
- Keyboard navigation support
- Focus management and indicators
- Screen reader friendly status labels
- Color + icon dual indication (not color-only)
- High contrast colors
- Live regions for dynamic content

## Authentication

The frontend uses JWT-based authentication:
- Login via `/login` page
- Token stored in localStorage
- API client automatically includes authentication headers
- Permission-based UI access control

## API Communication

All API calls go through the centralized API client (`src/lib/api/client.ts`):
- Automatic token management
- Type-safe request/response handling
- Consistent error handling
- Environment-based configuration
- Enhanced error types for different failure scenarios

### Error Handling

The API client includes comprehensive error handling with specific error types:

- **NetworkError**: Network connectivity issues
- **AuthenticationError**: 401 Unauthorized responses (clears invalid tokens)
- **AuthorizationError**: 403 Forbidden responses
- **NotFoundError**: 404 Not Found responses
- **ValidationError**: 400/409 validation errors with details
- **RateLimitError**: 429 Too Many Requests
- **ServerError**: 500+ server errors
- **ApiRequestError**: Generic API request errors

All errors provide user-friendly messages while preserving detailed information for debugging.

### Safe Rendering

Untrusted API data is rendered safely using utilities from `src/lib/safe-rendering/`:

- **safeText**: Escapes HTML entities to prevent XSS
- **truncateText**: Safely truncates long content
- **safeDate**: Formats timestamps safely
- **safeJson**: Renders JSON data safely
- **isSuspiciousContent**: Detects potentially malicious content
- **sanitizeHtml**: Removes dangerous HTML elements
- **safeMarkdown**: Converts markdown to safe HTML
- **maskSensitive**: Masks sensitive information like tokens
- **safeEmail**: Renders email addresses safely
- **safeUrl**: Renders URLs safely
- **safeErrorMessage**: Sanitizes error messages

### CORS Configuration

The backend is configured to allow requests from the frontend development server:

- Development origins: `http://localhost:3000`, `http://127.0.0.1:3000`
- Configurable via backend CORS settings
- Secure for production deployment

### Loading States

All API-driven pages support consistent state handling:

- **Loading**: Shows loading spinner during API calls
- **Success**: Displays data when successfully loaded
- **Empty**: Shows empty state when no data is available
- **Error**: Displays user-friendly error messages with retry options

### Page Integration

All main pages are integrated with real API calls:

- **Dashboard**: Fetches statistics and recent activity
- **Findings**: Retrieves security findings with filtering
- **Events**: Loads security event stream
- **Detections**: Manages detection rules with seeding capability
- **Health**: Monitors system health status

## Security Considerations

- Backend authorization is authoritative (frontend checks are UX only)
- No secrets committed to repository
- Environment variables for sensitive configuration
- Safe rendering of untrusted content
- Proper error handling without exposing sensitive information

## Development Notes

- This project uses the Next.js App Router (not Pages Router)
- Components are server components by default (use 'use client' for interactivity)
- API calls should use the centralized API client
- Follow the existing component patterns for consistency
- Add tests for new components and utilities
- Dashboard components are modular and reusable
- All dashboard sections support loading, error, and empty states
- Keyboard navigation is supported throughout the dashboard
- Dashboard follows accessibility best practices (ARIA labels, semantic HTML)