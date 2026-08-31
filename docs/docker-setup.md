# Docker Development Environment

This document describes how to set up and use the Docker-based development environment for Sentinel.

## Overview

The Docker environment provides a reproducible development setup with the following services:

- **PostgreSQL**: Database server
- **Backend**: FastAPI backend service
- **Frontend**: Next.js frontend application

All services are coordinated through Docker Compose and communicate via a dedicated Docker network.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/kzyarou/Sentinel.git
   cd Sentinel
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration if needed
   ```

3. **Start the development stack**
   ```bash
   docker compose up -d
   ```

4. **Wait for services to be healthy**
   ```bash
   docker compose ps
   ```
   All services should show "healthy" status.

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Services

### PostgreSQL

- **Image**: postgres:15-alpine
- **Port**: Internal only (not exposed to host)
- **Volume**: `postgres_data` for persistent storage
- **Health Check**: Uses `pg_isready` to verify database readiness

### Backend

- **Context**: `./backend`
- **Port**: 8000 (exposed to host)
- **Environment**: Configured via environment variables
- **Health Check**: Calls `/api/v1/health` endpoint
- **Dependencies**: PostgreSQL (waits for healthy status)
- **Hot Reload**: Enabled with `--reload` flag

### Frontend

- **Context**: `./frontend`
- **Port**: 3000 (exposed to host)
- **Environment**: Configured via environment variables
- **Health Check**: Calls root endpoint
- **Dependencies**: Backend (waits for healthy status)
- **Hot Reload**: Enabled via volume mounts

## Environment Variables

### Required Variables

The following environment variables are configured in `.env.example`:

```bash
# PostgreSQL
POSTGRES_USER=sentinel
POSTGRES_PASSWORD=sentinel
POSTGRES_DB=sentinel

# Backend
BACKEND_PORT=8000
DATABASE_URL=postgresql+asyncpg://sentinel:sentinel@postgres:5432/sentinel
SECRET_KEY=change-this-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Frontend
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### AI Provider Configuration (Optional)

If you want to enable AI analysis features, add these variables to `.env`:

```bash
AI_PROVIDER=openai
AI_API_KEY=your-api-key-here
AI_MODEL=gpt-4
AI_TIMEOUT=30
AI_MAX_RETRIES=3
```

## Common Operations

### Start Services

```bash
docker compose up -d
```

### Stop Services

```bash
docker compose down
```

### Stop Services and Remove Volumes

```bash
docker compose down -v
```

**Warning**: This will delete all database data.

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### Restart Services

```bash
# All services
docker compose restart

# Specific service
docker compose restart backend
```

### Rebuild Services

```bash
# All services
docker compose up -d --build

# Specific service
docker compose up -d --build backend
```

### Execute Commands in Containers

```bash
# Backend container
docker compose exec backend bash

# Frontend container
docker compose exec frontend sh

# PostgreSQL container
docker compose exec postgres psql -U sentinel -d sentinel
```

## Database Management

### Run Migrations

```bash
docker compose exec backend alembic upgrade head
```

### Reset Database

```bash
# Stop services and remove volumes
docker compose down -v

# Start services
docker compose up -d

# Run migrations
docker compose exec backend alembic upgrade head
```

### Access Database

```bash
docker compose exec postgres psql -U sentinel -d sentinel
```

### Backup Database

```bash
docker compose exec postgres pg_dump -U sentinel sentinel > backup.sql
```

### Restore Database

```bash
docker compose exec -T postgres psql -U sentinel sentinel < backup.sql
```

## Troubleshooting

### Services Not Starting

1. Check service status:
   ```bash
   docker compose ps
   ```

2. View logs for errors:
   ```bash
   docker compose logs
   ```

3. Check port conflicts:
   ```bash
   # Make sure ports 3000 and 8000 are not in use
   netstat -tuln | grep -E '3000|8000'
   ```

### Database Connection Issues

1. Verify PostgreSQL is healthy:
   ```bash
   docker compose ps postgres
   ```

2. Check DATABASE_URL in `.env`:
   ```bash
   # Should be: postgresql+asyncpg://sentinel:sentinel@postgres:5432/sentinel
   ```

3. Test database connection:
   ```bash
   docker compose exec backend python -c "from app.db.session import engine; import asyncio; asyncio.run(engine.connect())"
   ```

### Hot Reload Not Working

1. Verify volume mounts are correct:
   ```bash
   docker compose config
   ```

2. Check if node_modules volume is mounted:
   ```bash
   docker compose exec frontend ls -la /app/node_modules
   ```

3. Restart the specific service:
   ```bash
   docker compose restart frontend
   ```

### Permission Issues

If you encounter permission issues with created files:

```bash
# Fix ownership of mounted volumes
sudo chown -R $USER:$USER backend frontend
```

## Architecture

```
┌─────────────────────────────────────────┐
│              Docker Network             │
│                                         │
│  ┌─────────────┐      ┌─────────────┐   │
│  │  Frontend   │─────►│   Backend   │   │
│  │  Next.js    │      │   FastAPI   │   │
│  │  :3000      │      │   :8000     │   │
│  └─────────────┘      └──────┬──────┘   │
│                              │          │
│                              ▼          │
│                       ┌─────────────┐   │
│                       │ PostgreSQL  │   │
│                       │   :5432     │   │
│                       └─────────────┘   │
└─────────────────────────────────────────┘
```

## Security Considerations

### Development Environment

- Default credentials are used for development only
- Database is not exposed to external networks
- CORS is configured for local development

### Production Deployment

Before deploying to production:

1. **Change all default passwords and secrets**
2. **Use strong, randomly generated values for:**
   - `POSTGRES_PASSWORD`
   - `SECRET_KEY`
   - `AI_API_KEY` (if using AI features)
3. **Update CORS origins** to production frontend URLs
4. **Use environment-specific configuration**
5. **Enable SSL/TLS** for database connections
6. **Use separate environments** for development, staging, and production

### Secrets Management

Never commit secrets to the repository. Use:

- Environment variables
- Docker secrets (for swarm mode)
- Secret management services (AWS Secrets Manager, HashiCorp Vault, etc.)

## Performance Tuning

### Resource Limits

You can add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Database Performance

For better database performance:

1. Increase PostgreSQL shared buffers:
   ```yaml
   postgres:
     command:
       - "postgres"
       - "-c"
       - "shared_buffers=256MB"
   ```

2. Use a PostgreSQL image optimized for your workload

## Advanced Configuration

### Custom Docker Compose Overrides

Create `docker-compose.override.yml` for local customizations:

```yaml
services:
  backend:
    volumes:
      - ./backend/logs:/app/logs
  frontend:
    environment:
      - NEXT_PUBLIC_ENABLE_DEBUG_MODE=true
```

### Multiple Environments

Create separate compose files for different environments:

```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Cleaning Up

### Remove All Containers

```bash
docker compose down --remove-orphans
```

### Remove All Images

```bash
docker compose down --rmi all
```

### Remove All Volumes

```bash
docker compose down -v
```

### Full Cleanup

```bash
docker compose down --remove-orphans --rmi all -v
```

**Warning**: This will remove all containers, images, and volumes associated with the project.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review Docker logs: `docker compose logs`
3. Check service health: `docker compose ps`
4. Consult the main project documentation

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)