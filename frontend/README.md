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
│   │   └── validation/         # Form validation
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