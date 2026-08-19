# Sentinel Backend

FastAPI backend for the Sentinel cybersecurity monitoring platform.

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints and routing
│   ├── core/          # Core configuration and utilities
│   ├── db/            # Database session and connection management
│   ├── models/        # SQLAlchemy ORM models
│   ├── schemas/       # Pydantic schemas for validation
│   ├── services/      # Business logic services
│   ├── detection/     # Detection engine and rules
│   └── main.py        # Application entry point
├── alembic/           # Database migrations
├── tests/             # Automated tests
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
pytest tests/test_health.py
```

## API Endpoints

### Health Check
- `GET /api/v1/health` - Basic health check endpoint
- `GET /api/v1/health/ready` - Readiness check with database connectivity

### Event Ingestion
- `POST /api/v1/events` - Ingest security events for processing
- `GET /api/v1/events/{event_id}` - Retrieve a specific event by ID

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
