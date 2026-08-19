# Sentinel Data Model Documentation

## Overview

This document describes the core data model for Sentinel's cybersecurity monitoring platform. The data model is designed to preserve relationships between telemetry, detections, findings, evidence, AI analysis, users, and audit records while maintaining traceability, auditability, and referential integrity.

## Entity Relationship Diagram

```
Event
  │
  ▼
Detection
  │
  ├──────────────► Detection Rule
  │
  ▼
Finding
  │
  ├──────────────► Evidence
  │
  └──────────────► AI Analysis

User
  │
  └──────────────► Audit Log
```

## Core Entities

### Event

Represents normalized telemetry received by Sentinel.

**Table:** `events`

**Fields:**
- `id` (String, PK): Unique event identifier (UUID)
- `event_type` (String): Type of event (e.g., login_attempt, file_access)
- `source` (String): Source of the event (e.g., ssh, windows_logs)
- `timestamp` (DateTime): When the event occurred
- `host` (String, nullable): Hostname where event occurred
- `user` (String, nullable): User/entity involved in event
- `normalized_data` (JSON, nullable): Normalized event data
- `raw_data` (Text, nullable): Original event data (preserved per ADR-005)
- `ingestion_timestamp` (DateTime): When Sentinel received the event

**Indexes:**
- `idx_events_source_timestamp`: (source, timestamp)
- `idx_events_type_timestamp`: (event_type, timestamp)
- `idx_events_host_timestamp`: (host, timestamp)

**Relationships:**
- One-to-many: Event → Detection
- One-to-many: Event → Evidence

**Design Notes:**
- Preserves original event data for auditability (ADR-005)
- Uses JSON for flexible normalized data structure
- Supports multiple event sources without schema changes

### Detection

Represents a rule or analytic condition that matched an event or group of events.

**Table:** `detections`

**Fields:**
- `id` (String, PK): Unique detection identifier (UUID)
- `detection_rule_id` (String, FK): Reference to detection rule
- `event_id` (String, FK): Reference to triggering event
- `detection_timestamp` (DateTime): When detection occurred
- `severity` (String): LOW, MEDIUM, HIGH, CRITICAL
- `confidence` (Integer): 0-100 confidence score
- `rule_version` (String): Version of rule that generated detection
- `detection_metadata` (JSON, nullable): Additional detection metadata

**Indexes:**
- `idx_detections_rule_timestamp`: (detection_rule_id, detection_timestamp)
- `idx_detections_severity_timestamp`: (severity, detection_timestamp)

**Relationships:**
- Many-to-one: Detection → DetectionRule
- Many-to-one: Detection → Event
- One-to-one: Detection → Finding

**Design Notes:**
- Stores rule version for historical traceability (ADR-009)
- Links detection to specific event for evidence preservation
- Separate from findings to maintain detection → finding → AI analysis flow

### Detection Rule

Represents a versioned security detection definition.

**Table:** `detection_rules`

**Fields:**
- `id` (String, PK): Unique rule identifier (UUID)
- `name` (String, unique): Human-readable rule name
- `description` (Text, nullable): Rule description
- `category` (String): Rule category (e.g., authentication, network)
- `severity` (String): Default severity for detections
- `version` (String): Rule version
- `enabled` (Boolean): Whether rule is active
- `rule_definition` (JSON): Rule logic/definition
- `created_timestamp` (DateTime): When rule was created
- `updated_timestamp` (DateTime): When rule was last updated

**Indexes:**
- `idx_detection_rules_category_enabled`: (category, enabled)
- `idx_detection_rules_severity_enabled`: (severity, enabled)

**Relationships:**
- One-to-many: DetectionRule → Detection

**Design Notes:**
- Supports versioned detection rules (ADR-009)
- Rule definition stored as JSON for flexibility
- Historical detections retain reference to specific rule version

### Finding

Represents a security-relevant result that can be investigated.

**Table:** `findings`

**Fields:**
- `id` (String, PK): Unique finding identifier (UUID)
- `title` (String): Human-readable finding title
- `description` (Text, nullable): Detailed description
- `severity` (String): LOW, MEDIUM, HIGH, CRITICAL
- `confidence` (Integer): 0-100 confidence score
- `status` (Enum): OPEN, INVESTIGATING, RESOLVED, FALSE_POSITIVE
- `created_timestamp` (DateTime): When finding was created
- `updated_timestamp` (DateTime): When finding was last updated
- `detection_id` (String, FK, nullable): Reference to triggering detection

**Indexes:**
- `idx_findings_status_timestamp`: (status, created_timestamp)
- `idx_findings_severity_timestamp`: (severity, created_timestamp)

**Relationships:**
- Many-to-one: Finding → Detection
- One-to-many: Finding → Evidence
- One-to-many: Finding → AIAnalysis

**Design Notes:**
- Central entity for security investigations
- Status tracking for investigation workflow
- Links to evidence and AI analysis
- Can exist without detection (manual findings)

### Evidence

Represents information supporting a detection or finding.

**Table:** `evidence`

**Fields:**
- `id` (String, PK): Unique evidence identifier (UUID)
- `finding_id` (String, FK): Reference to associated finding
- `event_id` (String, FK, nullable): Reference to source event
- `evidence_type` (String): Type of evidence (e.g., log_entry, file_hash)
- `evidence_content` (JSON): Evidence data
- `created_timestamp` (DateTime): When evidence was created

**Indexes:**
- `idx_evidence_finding_timestamp`: (finding_id, created_timestamp)
- `idx_evidence_type_timestamp`: (evidence_type, created_timestamp)

**Relationships:**
- Many-to-one: Evidence → Finding
- Many-to-one: Evidence → Event

**Design Notes:**
- Maintains traceability back to original events (ADR-005)
- Supports multiple evidence types
- Evidence is authoritative security data

### AI Analysis

Represents advisory analysis generated from an existing finding.

**Table:** `ai_analyses`

**Fields:**
- `id` (String, PK): Unique analysis identifier (UUID)
- `finding_id` (String, FK): Reference to analyzed finding
- `provider` (String): AI provider (e.g., openai, anthropic)
- `model` (String): AI model used
- `prompt_version` (String, nullable): Version of prompt used
- `analysis_result` (JSON): AI analysis output
- `created_timestamp` (DateTime): When analysis was created
- `status` (Enum): PENDING, PROCESSING, COMPLETED, FAILED

**Indexes:**
- `idx_ai_analyses_finding_timestamp`: (finding_id, created_timestamp)
- `idx_ai_analyses_status_timestamp`: (status, created_timestamp)

**Relationships:**
- Many-to-one: AIAnalysis → Finding

**Design Notes:**
- AI analysis is non-authoritative (ADR-008)
- Separated from authoritative detection evidence
- Supports multiple AI analyses per finding
- Tracks prompt version for reproducibility

### User

Represents authenticated Sentinel users.

**Table:** `users`

**Fields:**
- `id` (String, PK): Unique user identifier (UUID)
- `external_id` (String, unique): External identity reference
- `username` (String, unique): Sentinel username
- `role` (Enum): ADMIN, ANALYST, VIEWER
- `status` (Enum): ACTIVE, INACTIVE, SUSPENDED
- `created_timestamp` (DateTime): When user was created
- `updated_timestamp` (DateTime): When user was last updated

**Indexes:**
- `idx_users_role_status`: (role, status)

**Relationships:**
- One-to-many: User → AuditLog

**Design Notes:**
- Credentials not stored directly (security requirement)
- Supports external identity providers
- Role-based access control
- Status tracking for user lifecycle

### Audit Log

Records security-sensitive user actions.

**Table:** `audit_logs`

**Fields:**
- `id` (String, PK): Unique audit log identifier (UUID)
- `user_id` (String, FK): Reference to user who performed action
- `action` (String): Action performed (e.g., CREATE, UPDATE, DELETE)
- `resource_type` (String): Type of resource affected
- `resource_id` (String, nullable): ID of specific resource
- `timestamp` (DateTime): When action occurred
- `request_id` (String, nullable): Request identifier for correlation
- `audit_metadata` (JSON, nullable): Additional audit metadata

**Indexes:**
- `idx_audit_logs_user_timestamp`: (user_id, timestamp)
- `idx_audit_logs_action_timestamp`: (action, timestamp)
- `idx_audit_logs_resource_timestamp`: (resource_type, resource_id, timestamp)

**Relationships:**
- Many-to-one: AuditLog → User

**Design Notes:**
- Supports investigation and accountability
- Request ID enables correlation across logs
- Tracks who did what to which resource when

## Data Integrity

### Constraints

- **Primary Keys**: All tables have UUID primary keys
- **Foreign Keys**: Enforce referential integrity between related entities
- **Unique Constraints**: Ensure uniqueness where required (e.g., usernames, rule names)
- **NOT NULL Constraints**: Critical fields cannot be null
- **Check Constraints**: Enum fields restrict to valid values
- **Indexes**: Optimize common query patterns

### Relationships

The model enforces the following relationships to prevent orphaned records:

- Detections must reference valid DetectionRules and Events
- Findings can reference Detections (optional)
- Evidence must reference valid Findings
- Evidence can reference Events (optional)
- AI Analyses must reference valid Findings
- Audit Logs must reference valid Users

Cascade delete is configured where appropriate:
- Deleting a Finding cascades to Evidence and AI Analyses
- Deleting a User cascades to Audit Logs

## Data Flow

1. **Event Ingestion**: Events are ingested and stored with original data preserved
2. **Detection**: Events are evaluated against DetectionRules, creating Detections
3. **Finding**: Detections (or manual actions) create Findings for investigation
4. **Evidence**: Evidence is linked to Findings, maintaining traceability to Events
5. **AI Analysis**: AI Analyses are generated for Findings, providing advisory context
6. **Audit**: User actions are logged for accountability

## Security Considerations

- **Original Data Preservation**: Raw event data is preserved (ADR-005)
- **AI Non-Authoritative**: AI analysis is separate from authoritative evidence (ADR-008)
- **Rule Versioning**: Historical detections retain rule version references (ADR-009)
- **User Access**: No credentials stored; supports external identity providers
- **Audit Trail**: All security-sensitive actions are logged
- **Referential Integrity**: Foreign keys prevent orphaned security records

## Extensibility

The model is designed for extensibility:

- **JSON Fields**: Many fields use JSON for flexible data structures
- **Event Sources**: Event model supports multiple sources without schema changes
- **Evidence Types**: Evidence model supports various evidence types
- **AI Providers**: AI Analysis model supports multiple AI providers
- **Future Entities**: New entities can be added without disrupting existing structure

## Migration

The data model is version-controlled using Alembic migrations:

- Each schema change is a separate migration
- Migrations support both upgrade and downgrade
- Historical data is preserved through migrations
- Migration files are committed to the repository

## References

- ADR-003: Use PostgreSQL as the Primary Data Store
- ADR-005: Preserve Original Event Data
- ADR-008: Treat AI Output as Non-Authoritative
- ADR-009: Version Detection Rules
- Sentinel System Architecture: Sections 6, 9, 10, 11, 15
