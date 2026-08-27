# Sentinel

Sentinel is an AI-assisted cybersecurity monitoring platform designed to collect system and network telemetry, identify potentially suspicious behavior, and provide explainable security findings.

## Overview

Sentinel follows a modular, event-driven architecture. Security-relevant telemetry enters through an ingestion layer, is normalized into a common event format, processed by deterministic detection logic, and correlated into security findings. Findings can then be enriched and explained by the AI analysis layer before being persisted and presented through the web application.

## Goals

- Collect and normalize security-relevant system and network events
- Detect suspicious behavior using deterministic detection rules
- Correlate related events into meaningful security findings
- Use AI to provide contextual explanations of detected findings
- Provide evidence supporting each finding rather than relying solely on an AI-generated conclusion
- Provide a web dashboard for monitoring findings and system activity
- Maintain a comprehensive, auditable record of security events and user actions
- Design the system with clear security boundaries and least-privilege principles
- Provide automated tests for core detection and application logic
- Document architectural and security decisions throughout development

## Project Structure

```
sentinel/
├── backend/          # Backend services (FastAPI, detection engine, event processing)
├── frontend/         # Web interface (Next.js)
├── docs/             # Architecture documentation and ADRs
├── tests/            # Automated tests
├── infrastructure/   # Docker and deployment configurations
├── .gitignore
├── README.md
└── docker-compose.yml
```

## Architecture

The system is composed of the following core components:

- **Event Ingestion**: Receives and validates security-relevant telemetry
- **Event Normalization**: Converts different event sources into a consistent internal schema
- **Detection Engine**: Evaluates normalized events against deterministic rules and heuristics
- **Event Correlation**: Connects related events to identify patterns
- **Finding Store**: Persists events, detections, findings, and supporting evidence (PostgreSQL)
- **AI Analysis**: Provides contextual analysis and explanations
- **Audit Logging**: Comprehensive security audit logging with request correlation
- **REST API**: Provides authenticated access to Sentinel's backend capabilities (FastAPI)
- **Web Interface**: Provides monitoring, investigation, and visualization capabilities (Next.js)

## Getting Started

### Backend

The backend uses FastAPI with PostgreSQL. See `backend/README.md` for detailed setup instructions.

### Frontend

The frontend uses Next.js with TypeScript. See `frontend/README.md` for detailed setup instructions.

### Docker

This project uses Docker for reproducible development environments. See `docker-compose.yml` for service definitions.

## Security Dashboard

The Sentinel security dashboard provides analysts with a high-level view of the current security state without replacing the detailed investigation workflow.

### Dashboard Features

**Severity Metrics:**
- Critical, High, Medium, Low severity breakdown
- Total findings count
- Color-coded severity indicators with icons
- Accessibility-friendly (color + icon dual indication)

**Recent Findings:**
- List of recent security findings
- Severity and status badges
- Links to investigation views
- Configurable max items display
- Loading, error, and empty states

**System Health:**
- API status monitoring
- Database status monitoring
- Detection engine status monitoring
- Three status levels: Healthy, Degraded, Unavailable
- Last check timestamps

**Data Refresh:**
- Manual refresh button
- Last refresh timestamp display
- Optional auto-refresh (30-second intervals)
- Keyboard shortcut support (Ctrl/Cmd + R)

**Keyboard Navigation:**
- Ctrl/Cmd + R: Refresh dashboard
- Alt + F: Navigate to findings
- Alt + E: Navigate to events
- Alt + D: Navigate to detections
- Alt + H: Navigate to health

### Dashboard Accessibility

The dashboard follows accessibility best practices:

- Semantic HTML structure
- ARIA labels for all interactive elements
- Keyboard navigation support
- Focus management and indicators
- Screen reader friendly status labels
- Color + icon dual indication (not color-only)
- High contrast colors

## API Integration

The frontend and backend are integrated through a secure REST API with CORS configuration:

### Backend CORS Configuration

The backend is configured to allow requests from specific frontend origins:

- **Development**: `http://localhost:3000`, `http://127.0.0.1:3000`
- **Production**: Configurable via `CORS_ORIGINS` environment variable
- **Security**: Credentials enabled for JWT authentication
- **Configuration**: See `backend/README.md` for CORS environment variables

### Frontend API Client

The frontend uses a centralized API client with comprehensive error handling:

- **Error Types**: Network, Authentication, Authorization, Validation, Rate Limit, Server errors
- **Safe Rendering**: All API data is rendered safely to prevent XSS attacks
- **Loading States**: Consistent loading, success, empty, and error states across all pages
- **Environment Configuration**: Backend URL configurable via `NEXT_PUBLIC_API_URL`

### Frontend Pages with API Integration

All main pages are integrated with real API calls:

- **Dashboard**: Real-time statistics and recent activity with comprehensive monitoring
- **Findings**: Security findings with filtering and pagination
- **Events**: Security event stream with type categorization
- **Detections**: Detection rule management with seeding capability
- **Health**: System health monitoring

### Security Considerations

- **Backend Authorization**: All authorization is enforced by the backend
- **Safe Rendering**: Untrusted API data is rendered safely using dedicated utilities
- **Error Handling**: Generic user-facing errors without exposing sensitive information
- **CORS Security**: Restricted origins in production, credentials only when needed
- **Token Security**: JWT tokens stored securely in localStorage

## Documentation

Detailed architecture documentation and architectural decision records (ADRs) are available in the `docs/` directory:

- [Sentinel System Architecture](docs/Sentinel%20System%20Architecture.txt) - Complete system architecture
- [Data Model Documentation](docs/Data%20Model%20Documentation.md) - Core data model and relationships

## License

[To be determined]
