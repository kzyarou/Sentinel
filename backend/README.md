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
