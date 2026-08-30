# Detection Rule Management

## Overview

Detection rules are the core security logic of Sentinel. They define patterns and conditions that trigger security findings when matched against incoming telemetry. This document describes the detection rule management system, including versioning, validation, lifecycle management, and security constraints.

## Architecture

### Model

Detection rules are stored in the `detection_rules` table with the following structure:

- **id**: Unique identifier (UUID)
- **name**: Rule identifier (e.g., `auth-brute-force`)
- **description**: Human-readable description
- **category**: Rule category (enum)
- **severity**: Rule severity (enum)
- **version**: Rule version (e.g., `1.0`, `2.0`)
- **enabled**: Lifecycle state (enabled/disabled)
- **rule_definition**: Structured JSON rule definition
- **created_by**: User who created the rule
- **updated_by**: User who last modified the rule
- **created_timestamp**: Creation timestamp
- **updated_timestamp**: Last modification timestamp

### Versioning

Rules support explicit versioning through a composite unique constraint on `(name, version)`. This allows:

- Multiple versions of the same rule to coexist
- Historical detections to reference the exact rule version that generated them
- Rule evolution without silently altering historical interpretations

Example version hierarchy:
```
auth-brute-force
├── v1.0 (original rule)
├── v1.1 (minor refinement)
└── v2.0 (major logic change)
```

**Versioning Rules:**
- Rule name and version together must be unique
- Name and version cannot be changed after creation
- To update a rule, create a new version with the same name
- Historical detections retain reference to their original rule version

### Categories

Detection rules are categorized for organization and filtering:

- `AUTHENTICATION`: Authentication-related events (brute force, credential theft)
- `ACCESS_CONTROL`: Authorization and permission violations
- `NETWORK`: Network-based attacks and anomalies
- `PROCESS`: Process execution and manipulation
- `ENDPOINT`: Host-based security events
- `SYSTEM`: System-level security events
- `OTHER`: Miscellaneous security events

### Severity Levels

Rules are assigned severity levels to prioritize findings:

- `LOW`: Low-risk events, informational
- `MEDIUM`: Moderate risk, requires investigation
- `HIGH`: High risk, urgent investigation needed
- `CRITICAL`: Critical security events, immediate response required

### Lifecycle States

Rules have two lifecycle states:

- `ENABLED`: Rule is active and will generate detections
- `DISABLED`: Rule is inactive and will not generate new detections

**Lifecycle Rules:**
- Disabled rules do not generate new detections
- Disabling a rule does not delete historical detections
- Re-enabling a rule resumes detection generation
- Enable/disable operations are administrator-only and auditable

## Rule Definition Language

### Structure

Rule definitions use a structured JSON format with conditions:

```json
{
  "conditions": [
    {
      "field": "event.type",
      "operator": "equals",
      "value": "authentication_failure"
    },
    {
      "field": "event.source",
      "operator": "equals",
      "value": "ssh"
    }
  ]
}
```

### Supported Fields

The following event fields are supported in rule conditions:

- `event.type`: Event type identifier
- `event.source`: Event source system
- `event.host`: Hostname or IP address
- `event.user`: User identifier
- `event.ip_address`: IP address
- `event.process`: Process name
- `event.process_id`: Process ID
- `event.parent_process`: Parent process name
- `event.command_line`: Command line arguments
- `event.file_path`: File path
- `event.file_hash`: File hash
- `event.registry_key`: Registry key
- `event.registry_value`: Registry value
- `event.url`: URL
- `event.domain`: Domain name
- `event.protocol`: Network protocol
- `event.port`: Port number
- `event.mac_address`: MAC address
- `event.http_method`: HTTP method
- `event.http_status`: HTTP status code
- `event.http_url`: HTTP URL
- `event.http_user_agent`: HTTP user agent
- `event.http_referer`: HTTP referer
- `event.http_headers`: HTTP headers
- `event.ssh_user`: SSH username
- `event.ssh_method`: SSH authentication method
- `event.ssh_protocol`: SSH protocol version
- `event.ssh_client_version`: SSH client version
- `event.login_type`: Login type
- `event.login_result`: Login result
- `event.user_agent`: User agent string
- `event.email_subject`: Email subject
- `event.email_sender`: Email sender
- `event.email_recipient`: Email recipient
- `event.email_attachment`: Email attachment
- `event.dns_query`: DNS query
- `event.dns_query_type`: DNS query type
- `event.dns_response`: DNS response
- `event.certificate_subject`: Certificate subject
- `event.certificate_issuer`: Certificate issuer
- `event.certificate_serial`: Certificate serial number
- `event.certificate_fingerprint`: Certificate fingerprint
- `event.certificate_valid_from`: Certificate validity start
- `event.certificate_valid_to`: Certificate validity end

### Supported Operators

The following operators are supported in rule conditions:

- `equals`: Exact match
- `not_equals`: Does not match
- `contains`: Contains substring
- `not_contains`: Does not contain substring
- `starts_with`: Starts with substring
- `ends_with`: Ends with substring
- `greater_than`: Greater than
- `less_than`: Less than
- `greater_than_or_equal`: Greater than or equal
- `less_than_or_equal`: Less than or equal
- `in`: Value in list
- `not_in`: Value not in list
- `matches`: Regex match
- `exists`: Field exists
- `not_exists`: Field does not exist

### Example Rules

#### Simple Authentication Failure Rule
```json
{
  "conditions": [
    {
      "field": "event.type",
      "operator": "equals",
      "value": "authentication_failure"
    }
  ]
}
```

#### SSH Brute Force Rule
```json
{
  "conditions": [
    {
      "field": "event.type",
      "operator": "equals",
      "value": "authentication_failure"
    },
    {
      "field": "event.source",
      "operator": "equals",
      "value": "ssh"
    },
    {
      "field": "event.user",
      "operator": "not_equals",
      "value": "root"
    }
  ]
}
```

#### Suspicious Process Execution Rule
```json
{
  "conditions": [
    {
      "field": "event.type",
      "operator": "equals",
      "value": "process_execution"
    },
    {
      "field": "event.command_line",
      "operator": "contains",
      "value": "powershell.exe -encodedcommand"
    }
  ]
}
```

## Security Constraints

### No Arbitrary Code Execution

Detection rules use a structured definition language, not arbitrary code. The system:

- Validates rule definitions against known fields and operators
- Rejects unsupported operators and fields
- Rejects executable code patterns (e.g., `eval`, `exec`, `__import__`)
- Never executes user-provided code during rule evaluation
- Safely parses and validates JSON rule definitions

### Input Validation

All rule inputs are validated:

- Required fields must be present
- Enum values must be valid
- Rule identifiers must be alphanumeric with hyphens/underscores
- Rule definitions must be valid JSON
- Conditions must specify valid fields and operators
- Values must match expected types

### Authorization

The following authorization model is enforced:

**Analyst Role:**
- Can read rules
- Cannot create, update, enable, or disable rules

**Administrator Role:**
- Can read rules
- Can create rules
- Can update rules
- Can enable rules
- Can disable rules

Authorization is enforced by the backend API, not the frontend.

### Audit Logging

All sensitive rule operations generate audit events:

- `detection_rule.created`: Rule creation
- `detection_rule.updated`: Rule modification
- `detection_rule.enabled`: Rule enabled
- `detection_rule.disabled`: Rule disabled

Audit records include:
- Actor (user who performed the action)
- Rule ID and name
- Rule version
- Action performed
- Timestamp
- Request correlation ID

## API Endpoints

### List Rules
```
GET /api/v1/detection-rules
```

Returns a paginated list of detection rules.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50)
- `category`: Filter by category
- `severity`: Filter by severity
- `enabled`: Filter by enabled state
- `name`: Filter by rule name

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "auth-brute-force",
      "description": "Detect brute force authentication attempts",
      "category": "AUTHENTICATION",
      "severity": "HIGH",
      "version": "1.0",
      "enabled": true,
      "rule_definition": {...},
      "created_by": "user-id",
      "updated_by": "user-id",
      "created_timestamp": "2024-01-01T00:00:00Z",
      "updated_timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50
}
```

### Get Rule by ID
```
GET /api/v1/detection-rules/{rule_id}
```

Returns a specific detection rule by ID.

**Response:**
```json
{
  "id": "uuid",
  "name": "auth-brute-force",
  "description": "Detect brute force authentication attempts",
  "category": "AUTHENTICATION",
  "severity": "HIGH",
  "version": "1.0",
  "enabled": true,
  "rule_definition": {...},
  "created_by": "user-id",
  "updated_by": "user-id",
  "created_timestamp": "2024-01-01T00:00:00Z",
  "updated_timestamp": "2024-01-01T00:00:00Z"
}
```

### Get Rule by Name and Version
```
GET /api/v1/detection-rules/by-name/{rule_name}
```

Returns all versions of a rule by name.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "auth-brute-force",
    "version": "1.0",
    ...
  },
  {
    "id": "uuid",
    "name": "auth-brute-force",
    "version": "2.0",
    ...
  }
]
```

### Create Rule
```
POST /api/v1/detection-rules
```

Creates a new detection rule.

**Request Body:**
```json
{
  "name": "auth-brute-force",
  "description": "Detect brute force authentication attempts",
  "category": "AUTHENTICATION",
  "severity": "HIGH",
  "version": "1.0",
  "enabled": true,
  "rule_definition": {
    "conditions": [...]
  }
}
```

**Response:** Returns the created rule.

**Authorization:** Administrator only.

### Update Rule
```
PATCH /api/v1/detection-rules/{rule_id}
```

Updates an existing detection rule.

**Request Body:**
```json
{
  "description": "Updated description",
  "severity": "CRITICAL",
  "enabled": false
}
```

**Constraints:**
- Name and version cannot be changed
- Other fields can be updated

**Authorization:** Administrator only.

### Enable Rule
```
POST /api/v1/detection-rules/{rule_id}/enable
```

Enables a detection rule.

**Authorization:** Administrator only.

### Disable Rule
```
POST /api/v1/detection-rules/{rule_id}/disable
```

Disables a detection rule.

**Authorization:** Administrator only.

## Best Practices

### Rule Design

1. **Be Specific**: Use multiple conditions to reduce false positives
2. **Use Appropriate Severity**: Match severity to actual risk
3. **Version Frequently**: Create new versions for logic changes
4. **Document Well**: Clear descriptions help with investigation
5. **Test Thoroughly**: Validate rules against sample events

### Version Management

1. **Semantic Versioning**: Use semantic versioning (major.minor.patch)
2. **Backward Compatibility**: Consider impact on existing detections
3. **Gradual Rollout**: Test new versions before full deployment
4. **Keep Historical Versions**: Retain old versions for reference

### Security

1. **Validate Inputs**: Always validate rule definitions
2. **Limit Privileges**: Use least-privilege access
3. **Audit Changes**: Monitor rule modifications
4. **Review Regularly**: Periodically review rule effectiveness

## Integration with Detection Engine

Detection rules are consumed by the deterministic detection engine:

1. Engine queries enabled rules from the database
2. For each incoming event, engine evaluates rule conditions
3. Matches generate detection records with rule version reference
4. Findings are created from detections with AI analysis

Disabled rules are excluded from the evaluation process. Historical detections retain references to the exact rule version that generated them, ensuring traceability.

## Troubleshooting

### Rule Not Generating Detections

1. Check if rule is enabled
2. Verify rule definition syntax
3. Check event data matches expected fields
4. Review detection engine logs
5. Validate rule conditions with sample events

### Validation Errors

1. Check required fields are present
2. Verify enum values are valid
3. Ensure rule identifier is alphanumeric
4. Validate JSON structure
5. Check for unsupported operators/fields

### Performance Issues

1. Review rule complexity
2. Check database indexes
3. Optimize condition order
4. Consider rule categorization
5. Monitor detection engine performance

## References

- Detection Engine Documentation
- Event Schema Documentation
- API Documentation
- Audit Logging Documentation
- Authorization Documentation