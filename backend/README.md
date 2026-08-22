# Sentinel Backend

FastAPI backend for the Sentinel cybersecurity monitoring platform.

## Project Structure

```
backend/
├── app/
│   ├── ai/            # AI analysis system (providers, validation, error handling)
│   ├── api/           # API endpoints and routing
│   ├── core/          # Core configuration and utilities
│   ├── db/            # Database session and connection management
│   ├── models/        # SQLAlchemy ORM models
│   ├── schemas/       # Pydantic schemas for validation
│   ├── services/      # Business logic services
│   ├── detection/     # Detection engine and rules
│   ├── tests/         # Automated tests
│   └── main.py        # Application entry point
├── alembic/           # Database migrations
├── requirements.txt   # Production dependencies
├── requirements-dev.txt # Development dependencies
└── README.md          # This file
```

## Setup

### Prerequisites

- Python 3.11 or higher
- pip

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For development, install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Create environment configuration:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup

#### Using Docker (Recommended)

1. Start PostgreSQL using Docker Compose:
```bash
cd ..
docker compose up -d postgres
```

2. Run database migrations:
```bash
cd backend
alembic upgrade head
```

#### Manual PostgreSQL Setup

If you prefer to use a local PostgreSQL installation:

1. Install PostgreSQL
2. Create a database named `sentinel`
3. Update `DATABASE_URL` in your `.env` file
4. Run migrations:
```bash
alembic upgrade head
```

## Running the Application

### Development

Start the development server with auto-reload:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production

Start the production server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access:

- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json

## Testing

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest app/tests/test_ai_analysis.py
```

Run finding tests:
```bash
pytest tests/test_findings.py
```

## API Endpoints

### Health Check
- `GET /api/v1/health` - Basic health check endpoint
- `GET /api/v1/health/ready` - Readiness check with database connectivity

### Event Ingestion
- `POST /api/v1/events` - Ingest security events for processing
- `GET /api/v1/events/{event_id}` - Retrieve a specific event by ID

### Findings Management
- `GET /api/v1/findings` - Retrieve findings with filtering and pagination
- `GET /api/v1/findings/{finding_id}` - Retrieve a specific finding by ID
- `PATCH /api/v1/findings/{finding_id}` - Update a finding (status, fields)
- `GET /api/v1/findings/{finding_id}/detection` - Retrieve detection for a finding
- `GET /api/v1/findings/{finding_id}/evidence` - Retrieve evidence for a finding

### AI Analysis
- `POST /api/v1/findings/{finding_id}/analysis` - Trigger AI analysis for a finding
  - Request body: `{"force_refresh": boolean}` (optional)
  - Returns: Structured AI analysis with risk assessment, indicators, and investigation steps
  - Requires authentication and finding access authorization
- `GET /api/v1/findings/{finding_id}/analysis` - Retrieve existing AI analysis for a finding
  - Returns: Most recent AI analysis for the specified finding
  - Requires authentication and finding access authorization
- `GET /api/v1/ai-analysis/stats` - Get AI analysis error statistics (admin only)
  - Returns: Error statistics, success rates, and circuit breaker state
  - Requires admin role

#### Finding Endpoints

**GET /api/v1/findings**

Retrieve findings with optional filtering and pagination.

**Query Parameters:**
- `skip` (optional): Number of results to skip (default: 0)
- `limit` (optional): Maximum number of results to return (default: 100, max: 1000)
- `severity` (optional): Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
- `status` (optional): Filter by status (OPEN, INVESTIGATING, RESOLVED, FALSE_POSITIVE)

**Authentication:** Required (X-User-ID header)

**Response:**
```json
[
  {
    "id": "finding-id",
    "title": "Security Finding Title",
    "description": "Description of the finding",
    "severity": "HIGH",
    "confidence": 85,
    "status": "OPEN",
    "detection_id": "detection-id",
    "finding_metadata": {},
    "created_timestamp": "2024-01-01T00:00:00Z",
    "updated_timestamp": "2024-01-01T00:00:00Z"
  }
]
```

**PATCH /api/v1/findings/{finding_id}**

Update a finding. Status transitions are validated by the backend.

**Authentication:** Required (X-User-ID header)
**Authorization:** Role-based (admin, security_analyst, analyst can modify)

**Request Body:**
```json
{
  "status": "INVESTIGATING",
  "description": "Updated description"
}
```

**Valid Status Transitions:**
- OPEN → INVESTIGATING, FALSE_POSITIVE
- INVESTIGATING → RESOLVED, FALSE_POSITIVE, OPEN
- RESOLVED → OPEN, INVESTIGATING
- FALSE_POSITIVE → OPEN, INVESTIGATING

**Response:** Updated finding object

**Error Responses:**
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Finding not found
- `400 Bad Request` - Invalid status transition

#### Event Ingestion Endpoint

**POST /api/v1/events**

Ingests security telemetry from various sources, validates it, normalizes it, and persists it to the database.

**Request Body:**
```json
{
  "event_type": "ssh_login",
  "source": "ssh",
  "timestamp": "2024-01-01T00:00:00Z",
  "host": "server1.example.com",
  "user": "admin",
  "ip_address": "192.168.1.1"
}
```

**Required Fields:**
- `event_type` - Type of the security event (string, max 100 chars)
- `source` - Source of the event (string, max 100 chars)
- `timestamp` - Event timestamp in ISO 8601 format

**Optional Fields:**
- `host` - Hostname where the event occurred (string, max 255 chars)
- `user` - User associated with the event (string, max 255 chars)
- Additional source-specific fields (will be preserved in raw data)

**Response:**
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ingested"
}
```

**Error Responses:**
- `400 Bad Request` - Validation error (missing fields, invalid data types, invalid timestamps)
- `413 Payload Too Large` - Request payload exceeds 1MB limit
- `500 Internal Server Error` - Internal processing error (database or normalization failure)

**Supported Sources:**
- `ssh` - SSH authentication and command events
- `windows_logs` - Windows Event Log entries
- `syslog` - Syslog messages
- Custom sources will be normalized generically

**Validation Behavior:**
- Timestamps must be in ISO 8601 format
- Timestamps cannot be in the future
- Timestamps must be within the last 5 years
- Maximum payload size: 1MB
- Field length limits are enforced
- All input is sanitized to prevent injection attacks

**Security:**
- All external input is treated as untrusted
- SQL injection attempts are sanitized
- XSS attempts are mitigated
- Internal database errors are not exposed to clients
- Raw event data is preserved for investigation (ADR-005)
- Sensitive fields are not exposed in API responses

#### AI Analysis Response Structure
```json
{
  "id": "analysis-id",
  "finding_id": "finding-id",
  "provider_name": "mock",
  "model_name": "mock-model-v1",
  "model_version": "1.0.0",
  "summary": "Brief analysis summary",
  "observed_indicators": [
    {
      "type": "authentication",
      "description": "Indicator description",
      "confidence": 90
    }
  ],
  "possible_interpretation": "Analysis interpretation",
  "recommended_investigation_steps": ["Step 1", "Step 2"],
  "confidence_notes": "Confidence assessment",
  "risk_level": "HIGH",
  "urgency": "HIGH",
  "investigation_priority": "P1",
  "created_at": "2024-01-01T00:00:00Z",
  "metadata": {
    "validation_timestamp": "2024-01-01T00:00:00Z",
    "validation_version": "1.0.0"
  }
}
```

## Database Migrations

This project uses Alembic for database migrations.

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

## Configuration

Configuration is managed through environment variables. See `.env.example` for available options.

Key configuration:
- `APP_NAME` - Application name
- `APP_VERSION` - Application version
- `ENVIRONMENT` - Environment (development/production)
- `DEBUG` - Debug mode
- `API_V1_PREFIX` - API v1 prefix
- `DATABASE_URL` - Database connection string
- `MAX_PAYLOAD_SIZE` - Maximum request payload size in bytes (default: 1MB)

## Local Testing

### Testing Event Ingestion

Start the development server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Ingest a test event:
```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "ssh_login",
    "source": "ssh",
    "timestamp": "2024-01-01T00:00:00Z",
    "host": "server1.example.com",
    "user": "admin",
    "ip_address": "192.168.1.1"
  }'
```

Retrieve the ingested event:
```bash
curl http://localhost:8000/api/v1/events/{event_id}
```

### Payload Limitations

- Maximum request payload size: 1MB (configurable via `MAX_PAYLOAD_SIZE`)
- Oversized payloads are rejected with HTTP 413
- Field length limits are enforced (event_type: 100, host/user: 255 characters)

### Database Requirements

- PostgreSQL 12 or higher required
- Async PostgreSQL driver (asyncpg) for application connections
- Synchronous driver (psycopg2-binary) for Alembic migrations
- Database migrations must be applied before running the application

## Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server
- **PostgreSQL** - Relational database
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **AsyncPG** - Async PostgreSQL driver

## AI Analysis System

The Sentinel backend includes an AI-assisted finding analysis system that provides intelligent analysis of security findings.

### Architecture

The AI analysis system is built with the following components:

- **AI Provider Interface** (`app/ai/provider_interface.py`): Abstract interface for AI providers, enabling easy swapping between different AI services
- **Mock AI Provider** (`app/ai/mock_provider.py`): Reference implementation for testing and development
- **Prompt Constructor** (`app/ai/prompt_constructor.py`): Secure prompt generation with input sanitization to prevent prompt injection
- **Response Validator** (`app/ai/response_validator.py`): Structured validation of AI responses to ensure data quality
- **Error Handler** (`app/ai/error_handler.py`): Comprehensive error handling with circuit breaker pattern for reliability
- **AI Analysis Service** (`app/services/ai_analysis_service.py`): Orchestrates the complete AI analysis workflow

### Security Features

- **Prompt Injection Prevention**: Input sanitization removes common injection patterns before prompt construction
- **Circuit Breaker Pattern**: Prevents cascading failures when AI provider experiences issues
- **Structured Validation**: All AI responses are validated against expected schema
- **Access Control**: AI analysis endpoints require authentication and proper authorization
- **Error Isolation**: Different error types are handled appropriately to prevent system degradation

### Configuration

AI analysis system can be configured through the `AIAnalysisService` config parameter:

```python
config = {
    "enable_analysis": True,                    # Enable/disable AI analysis
    "max_retries": 2,                           # Maximum retry attempts
    "analysis_freshness_hours": 24,            # Hours before re-analysis
    "enable_circuit_breaker": True,             # Enable circuit breaker
    "circuit_breaker_threshold": 5,             # Failures before opening circuit
    "circuit_breaker_timeout": 60,             # Seconds before recovery attempt
    "max_prompt_length": 10000,                 # Maximum prompt length
    "enable_input_sanitization": True,          # Enable prompt injection prevention
    "max_evidence_items": 10                    # Maximum evidence items in prompt
}
```

### Extending with Real AI Providers

To add a real AI provider (e.g., OpenAI, Anthropic):

1. Create a new provider class implementing `AIProviderInterface`
2. Implement the `analyze_finding` method with your provider's API
3. Configure the service to use your provider instead of the mock

Example:
```python
from app.ai.provider_interface import AIProviderInterface

class OpenAIProvider(AIProviderInterface):
    async def analyze_finding(self, finding_data, evidence_data, detection_data):
        # Call OpenAI API here
        pass
    
    def get_provider_name(self):
        return "openai"
    
    def get_model_name(self):
        return "gpt-4"
    
    def get_version(self):
        return "1.0.0"
```

## Data Models

Sentinel uses SQLAlchemy ORM with the following core entities:

- **Event**: Normalized telemetry from various sources
- **Detection**: Rule matches against events
- **DetectionRule**: Versioned security detection definitions
- **Finding**: Security-relevant investigation results
- **Evidence**: Information supporting findings
- **AIAnalysis**: Advisory AI analysis of findings
- **User**: Authenticated Sentinel users
- **AuditLog**: Security-sensitive user actions

See [Data Model Documentation](../docs/Data%20Model%20Documentation.md) for detailed information about entities, relationships, and constraints.

## Services Architecture

The backend uses a service-oriented architecture for business logic:

### Event Services

- **EventValidator** (`app/services/validation.py`)
  - Validates incoming event data
  - Performs payload size validation
  - Sanitizes input to prevent injection attacks
  - Validates timestamps and field lengths
  - Enforces required field presence

- **EventNormalizer** (`app/services/normalization.py`)
  - Converts source-specific telemetry to common event model
  - Supports SSH, Windows, Syslog, and generic sources
  - Derives event types from source and content
  - Extracts and normalizes source-specific fields
  - Preserves original event data as JSON (ADR-005)

- **EventService** (`app/services/event_service.py`)
  - Handles event persistence and retrieval
  - Generates unique event IDs
  - Provides query methods (by ID, source, type, host)
  - Converts between models and schemas

### Finding Services

- **FindingService** (`app/services/finding_service.py`)
  - Manages finding CRUD operations and lifecycle
  - Validates and enforces status transitions
  - Creates findings from detections with metadata preservation
  - Manages finding-detection relationships
  - Integrates audit logging for security-sensitive actions
  - Supports filtering by severity and status

- **AuditService** (`app/services/audit_service.py`)
  - Creates audit log entries for security-sensitive actions
  - Logs finding status changes, resolutions, and false positive markings
  - Records modified fields and user context
  - Maintains audit trail for compliance and investigation

### Authorization Services

- **AuthorizationService** (`app/core/authorization.py`)
  - Handles authentication and authorization checks
  - Implements role-based access control (admin, security_analyst, analyst, viewer)
  - Enforces finding view and modify permissions
  - Provides backend-authorized access control (ADR-010)
  - Logs authorization failures for security monitoring

### Error Handling

- **Custom Exceptions** (`app/core/errors.py`)
  - `ValidationError` - Input validation failures
  - `NormalizationError` - Normalization processing failures
  - `PersistenceError` - Database operation failures
  - Consistent error responses without exposing internal details

### Middleware

- **PayloadSizeMiddleware** (`app/api/middleware.py`)
  - Validates request payload size before processing
  - Prevents resource exhaustion attacks
  - Configurable size limit via `MAX_PAYLOAD_SIZE`

## Development Guidelines

- Follow the existing project structure
- Use type hints for all functions
- Write tests for new features
- Keep configuration separate from application logic
- Never commit secrets or credentials
- Follow security best practices

## Security Considerations

- All external input is treated as untrusted
- Input validation is performed at API boundaries
- Configuration uses environment variables, not hardcoded values
- CORS is configured (restrict origins in production)
- No secrets are committed to the repository
- Database credentials are managed through environment variables
- Use strong, unique passwords for production databases
- Database access is restricted to application logic only (no direct frontend access)
- Use least-privileged database accounts
