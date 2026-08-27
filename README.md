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

## Finding Investigation View

The Sentinel finding investigation view provides analysts with a comprehensive interface for understanding and managing security findings.

### Investigation Route

- **Route**: `/findings/{finding_id}`
- **Dynamic routing**: Uses Next.js App Router with dynamic segments
- **Access**: Navigate from findings list or direct URL

### Investigation Components

**FindingSummary Component:**
- Displays finding title, description, severity, confidence, status
- Shows creation and update timestamps
- Displays detection category
- Color-coded severity and status badges with icons
- Authoritative vs AI content distinction
- Loading, error, and empty states
- Accessibility features (ARIA labels, semantic HTML)

**DetectionInfo Component:**
- Shows detection rule name and version
- Displays detection timestamp and severity
- Shows detection confidence
- Displays detection metadata
- Shows matched conditions
- Rule description display
- Loading, error, and empty states
- Color-coded severity indicators

**Evidence Component:**
- Displays related events as evidence
- Evidence tracing: Finding → Detection → Evidence → Original Event
- Collapsible event list with expandable details
- Event type and source badges
- Timestamp and host information
- Keyboard navigation support
- Loading, error, and empty states
- Evidence summary with count

**EventInformation Component:**
- Displays detailed event information
- Shows event type, source, timestamp, host
- Displays user/entity and IP address
- Shows normalized fields with JSON display
- Displays original event data with JSON display
- Safe rendering of untrusted event content
- Security notice for sensitive information
- Type-specific color coding

**AIAnalysis Component:**
- Clear visual distinction from authoritative evidence
- AI-generated content advisory notice
- Shows analysis summary and interpretation
- Displays observed indicators
- Shows investigation suggestions
- Displays uncertainty notes
- Confidence score with progress bar
- Model information display
- Analysis request functionality
- Loading, error, and empty states
- Retry capability for failed analysis
- "Analyze with AI" button for requesting analysis

**FindingStatus Component:**
- Displays current finding status
- Shows valid status transitions based on lifecycle
- Status change confirmation dialog
- Status lifecycle information
- Authorization notice
- Loading, error, and empty states
- Status change with backend validation

**StatusHistory Component:**
- Timeline view of status changes
- Shows previous and new status
- Displays change reason and actor
- Timestamp display
- Privacy notice for sensitive information
- Audit information display
- Loading, error, and empty states
- Proper ARIA labels for accessibility

### Investigation Features

**Authoritative vs AI Content Distinction:**
- Clear visual separation between authoritative evidence and AI analysis
- Color-coded sections (blue for authoritative, amber for AI)
- Advisory notices for AI-generated content
- "Content Type" labels

**Evidence Tracing:**
- Visual chain: Finding → Detection → Evidence → Original Event
- Expandable event details
- Related event linking
- Original data preservation

**Status Management:**
- Valid status transitions enforced
- Confirmation dialogs for status changes
- Status history timeline
- Backend authorization enforcement

**AI Analysis Integration:**
- Request AI analysis from investigation view
- Processing state indication
- Failed analysis handling with retry
- Detailed analysis display with multiple sections
- Confidence scoring

### Investigation Accessibility

**Semantic HTML:**
- Proper section elements with aria-label
- Role attributes where appropriate
- Semantic button and link elements
- Time elements for timestamps

**ARIA Support:**
- ARIA labels for all interactive elements
- aria-expanded for collapsible sections
- aria-live for dynamic content
- aria-pressed for toggle buttons
- Role="progressbar" for confidence scores
- Role="alert" for error messages

**Keyboard Navigation:**
- Full keyboard navigation support
- Focus management with visible indicators
- Enter and Space key support for expandable sections
- Tab order appropriate
- Keyboard shortcuts for common actions

**Visual Accessibility:**
- Color + icon dual indication (not color-only)
- High contrast colors for all indicators
- Readable font sizes and contrast
- Distinct status indicators
- Clear visual separation of content types

### Investigation Security

**Backend Authorization:**
- All API calls enforce backend permissions
- Status changes validated by backend
- AI analysis requests require authorization
- Unauthorized access handled gracefully

**Safe Rendering:**
- All event data rendered safely
- Sensitive fields filtered
- Original data displayed safely
- AI content clearly labeled as non-authoritative

**Error Handling:**
- Generic user-facing errors
- No backend stack traces exposed
- Proper error state display
- Retry functionality where appropriate

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
