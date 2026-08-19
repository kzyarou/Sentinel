import pytest
from datetime import datetime
from app.schemas import (
    EventCreate, EventUpdate, Event,
    DetectionCreate, DetectionUpdate, Detection,
    DetectionRuleCreate, DetectionRuleUpdate, DetectionRule,
    FindingCreate, FindingUpdate, Finding, FindingStatus,
    EvidenceCreate, EvidenceUpdate, Evidence,
    AIAnalysisCreate, AIAnalysisUpdate, AIAnalysis, AIAnalysisStatus,
    UserCreate, UserUpdate, User, UserRole, UserStatus,
    AuditLogCreate, AuditLogUpdate, AuditLog
)


def test_event_schemas():
    """Test Event schemas work correctly."""
    event_data = {
        "event_type": "login_attempt",
        "source": "ssh",
        "timestamp": datetime.now(),
        "host": "server1",
        "user": "admin",
        "normalized_data": {"ip": "192.168.1.1"},
        "raw_data": "original log data"
    }
    
    # Test creation
    event_create = EventCreate(**event_data)
    assert event_create.event_type == "login_attempt"
    assert event_create.source == "ssh"
    
    # Test update
    event_update = EventUpdate(event_type="logout")
    assert event_update.event_type == "logout"
    
    # Test serialization
    event_dict = event_create.model_dump()
    assert "event_type" in event_dict


def test_detection_schemas():
    """Test Detection schemas work correctly."""
    detection_data = {
        "detection_rule_id": "rule-123",
        "event_id": "event-456",
        "severity": "HIGH",
        "confidence": 85,
        "rule_version": "1.0",
        "detection_metadata": {"key": "value"}
    }
    
    detection_create = DetectionCreate(**detection_data)
    assert detection_create.detection_rule_id == "rule-123"
    assert detection_create.confidence == 85
    
    # Test confidence validation
    with pytest.raises(ValueError):
        DetectionCreate(**{**detection_data, "confidence": 150})


def test_detection_rule_schemas():
    """Test DetectionRule schemas work correctly."""
    rule_data = {
        "name": "Brute Force Detection",
        "description": "Detects brute force attempts",
        "category": "authentication",
        "severity": "HIGH",
        "version": "1.0",
        "enabled": True,
        "rule_definition": {"pattern": "failed_login > 5"}
    }
    
    rule_create = DetectionRuleCreate(**rule_data)
    assert rule_create.name == "Brute Force Detection"
    assert rule_create.enabled is True


def test_finding_schemas():
    """Test Finding schemas work correctly."""
    finding_data = {
        "title": "Suspicious Login Activity",
        "description": "Multiple failed login attempts detected",
        "severity": "HIGH",
        "confidence": 90,
        "status": FindingStatus.OPEN,
        "detection_id": "detection-123"
    }
    
    finding_create = FindingCreate(**finding_data)
    assert finding_create.title == "Suspicious Login Activity"
    assert finding_create.status == FindingStatus.OPEN
    
    # Test confidence validation
    with pytest.raises(ValueError):
        FindingCreate(**{**finding_data, "confidence": 150})


def test_evidence_schemas():
    """Test Evidence schemas work correctly."""
    evidence_data = {
        "finding_id": "finding-123",
        "event_id": "event-456",
        "evidence_type": "log_entry",
        "evidence_content": {"timestamp": "2024-01-01", "message": "failed login"}
    }
    
    evidence_create = EvidenceCreate(**evidence_data)
    assert evidence_create.evidence_type == "log_entry"
    assert evidence_create.finding_id == "finding-123"


def test_ai_analysis_schemas():
    """Test AIAnalysis schemas work correctly."""
    analysis_data = {
        "finding_id": "finding-123",
        "provider": "openai",
        "model": "gpt-4",
        "prompt_version": "1.0",
        "analysis_result": {"risk": "high", "explanation": "pattern detected"},
        "status": AIAnalysisStatus.COMPLETED
    }
    
    analysis_create = AIAnalysisCreate(**analysis_data)
    assert analysis_create.provider == "openai"
    assert analysis_create.status == AIAnalysisStatus.COMPLETED


def test_user_schemas():
    """Test User schemas work correctly."""
    user_data = {
        "external_id": "user-123",
        "username": "jdoe",
        "role": UserRole.ANALYST,
        "status": UserStatus.ACTIVE
    }
    
    user_create = UserCreate(**user_data)
    assert user_create.username == "jdoe"
    assert user_create.role == UserRole.ANALYST


def test_audit_log_schemas():
    """Test AuditLog schemas work correctly."""
    audit_data = {
        "user_id": "user-123",
        "action": "CREATE",
        "resource_type": "Finding",
        "resource_id": "finding-456",
        "request_id": "req-789",
        "audit_metadata": {"ip": "192.168.1.1"}
    }
    
    audit_create = AuditLogCreate(**audit_data)
    assert audit_create.action == "CREATE"
    assert audit_create.resource_type == "Finding"


def test_schema_field_validation():
    """Test schema field validation."""
    # Test max length constraints
    with pytest.raises(ValueError):
        EventCreate(
            event_type="a" * 101,  # Exceeds max_length=100
            source="ssh",
            timestamp=datetime.now()
        )
    
    with pytest.raises(ValueError):
        DetectionRuleCreate(
            name="a" * 256,  # Exceeds max_length=255
            category="authentication",
            severity="HIGH",
            version="1.0",
            rule_definition={}
        )


def test_schema_optional_fields():
    """Test optional fields work correctly."""
    # Event with minimal required fields
    event_minimal = EventCreate(
        event_type="test",
        source="test",
        timestamp=datetime.now()
    )
    assert event_minimal.host is None
    assert event_minimal.user is None
    
    # Detection with optional metadata
    detection_minimal = DetectionCreate(
        detection_rule_id="rule-1",
        event_id="event-1",
        severity="MEDIUM",
        confidence=50,
        rule_version="1.0"
    )
    assert detection_minimal.detection_metadata is None
