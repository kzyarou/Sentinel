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

## Documentation

Detailed architecture documentation and architectural decision records (ADRs) are available in the `docs/` directory:

- [Sentinel System Architecture](docs/Sentinel%20System%20Architecture.txt) - Complete system architecture
- [Data Model Documentation](docs/Data%20Model%20Documentation.md) - Core data model and relationships

## License

[To be determined]
