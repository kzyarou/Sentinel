import pytest
from app.models import (
    Event, Detection, DetectionRule, Finding, Evidence, 
    AIAnalysis, User, AuditLog, FindingStatus, AIAnalysisStatus, 
    UserRole, UserStatus
)


def test_event_model_structure():
    """Test Event model has expected attributes."""
    assert hasattr(Event, 'id')
    assert hasattr(Event, 'event_type')
    assert hasattr(Event, 'source')
    assert hasattr(Event, 'timestamp')
    assert hasattr(Event, 'host')
    assert hasattr(Event, 'user')
    assert hasattr(Event, 'normalized_data')
    assert hasattr(Event, 'raw_data')
    assert hasattr(Event, 'ingestion_timestamp')
    assert hasattr(Event, 'detections')


def test_detection_model_structure():
    """Test Detection model has expected attributes."""
    assert hasattr(Detection, 'id')
    assert hasattr(Detection, 'detection_rule_id')
    assert hasattr(Detection, 'event_id')
    assert hasattr(Detection, 'detection_timestamp')
    assert hasattr(Detection, 'severity')
    assert hasattr(Detection, 'confidence')
    assert hasattr(Detection, 'rule_version')
    assert hasattr(Detection, 'detection_metadata')
    assert hasattr(Detection, 'detection_rule')
    assert hasattr(Detection, 'event')
    assert hasattr(Detection, 'finding')


def test_detection_rule_model_structure():
    """Test DetectionRule model has expected attributes."""
    assert hasattr(DetectionRule, 'id')
    assert hasattr(DetectionRule, 'name')
    assert hasattr(DetectionRule, 'description')
    assert hasattr(DetectionRule, 'category')
    assert hasattr(DetectionRule, 'severity')
    assert hasattr(DetectionRule, 'version')
    assert hasattr(DetectionRule, 'enabled')
    assert hasattr(DetectionRule, 'rule_definition')
    assert hasattr(DetectionRule, 'created_timestamp')
    assert hasattr(DetectionRule, 'updated_timestamp')
    assert hasattr(DetectionRule, 'detections')


def test_finding_model_structure():
    """Test Finding model has expected attributes."""
    assert hasattr(Finding, 'id')
    assert hasattr(Finding, 'title')
    assert hasattr(Finding, 'description')
    assert hasattr(Finding, 'severity')
    assert hasattr(Finding, 'confidence')
    assert hasattr(Finding, 'status')
    assert hasattr(Finding, 'created_timestamp')
    assert hasattr(Finding, 'updated_timestamp')
    assert hasattr(Finding, 'detection_id')
    assert hasattr(Finding, 'detection')
    assert hasattr(Finding, 'evidence')
    assert hasattr(Finding, 'ai_analyses')


def test_evidence_model_structure():
    """Test Evidence model has expected attributes."""
    assert hasattr(Evidence, 'id')
    assert hasattr(Evidence, 'finding_id')
    assert hasattr(Evidence, 'event_id')
    assert hasattr(Evidence, 'evidence_type')
    assert hasattr(Evidence, 'evidence_content')
    assert hasattr(Evidence, 'created_timestamp')
    assert hasattr(Evidence, 'finding')
    assert hasattr(Evidence, 'event')


def test_ai_analysis_model_structure():
    """Test AIAnalysis model has expected attributes."""
    assert hasattr(AIAnalysis, 'id')
    assert hasattr(AIAnalysis, 'finding_id')
    assert hasattr(AIAnalysis, 'provider')
    assert hasattr(AIAnalysis, 'model')
    assert hasattr(AIAnalysis, 'prompt_version')
    assert hasattr(AIAnalysis, 'analysis_result')
    assert hasattr(AIAnalysis, 'created_timestamp')
    assert hasattr(AIAnalysis, 'status')
    assert hasattr(AIAnalysis, 'finding')


def test_user_model_structure():
    """Test User model has expected attributes."""
    assert hasattr(User, 'id')
    assert hasattr(User, 'external_id')
    assert hasattr(User, 'username')
    assert hasattr(User, 'role')
    assert hasattr(User, 'status')
    assert hasattr(User, 'created_timestamp')
    assert hasattr(User, 'updated_timestamp')
    assert hasattr(User, 'audit_logs')


def test_audit_log_model_structure():
    """Test AuditLog model has expected attributes."""
    assert hasattr(AuditLog, 'id')
    assert hasattr(AuditLog, 'user_id')
    assert hasattr(AuditLog, 'action')
    assert hasattr(AuditLog, 'resource_type')
    assert hasattr(AuditLog, 'resource_id')
    assert hasattr(AuditLog, 'timestamp')
    assert hasattr(AuditLog, 'request_id')
    assert hasattr(AuditLog, 'audit_metadata')
    assert hasattr(AuditLog, 'user')


def test_enums():
    """Test enum values are defined correctly."""
    assert FindingStatus.OPEN == "OPEN"
    assert FindingStatus.INVESTIGATING == "INVESTIGATING"
    assert FindingStatus.RESOLVED == "RESOLVED"
    assert FindingStatus.FALSE_POSITIVE == "FALSE_POSITIVE"
    
    assert AIAnalysisStatus.PENDING == "PENDING"
    assert AIAnalysisStatus.PROCESSING == "PROCESSING"
    assert AIAnalysisStatus.COMPLETED == "COMPLETED"
    assert AIAnalysisStatus.FAILED == "FAILED"
    
    assert UserRole.ADMIN == "ADMIN"
    assert UserRole.ANALYST == "ANALYST"
    assert UserRole.VIEWER == "VIEWER"
    
    assert UserStatus.ACTIVE == "ACTIVE"
    assert UserStatus.INACTIVE == "INACTIVE"
    assert UserStatus.SUSPENDED == "SUSPENDED"


def test_model_relationships():
    """Test model relationships are properly defined."""
    # Detection should have relationships
    assert hasattr(Detection, 'detection_rule')
    assert hasattr(Detection, 'event')
    
    # Finding should have relationships
    assert hasattr(Finding, 'detection')
    assert hasattr(Finding, 'evidence')
    assert hasattr(Finding, 'ai_analyses')
    
    # Evidence should have relationships
    assert hasattr(Evidence, 'finding')
    assert hasattr(Evidence, 'event')
    
    # AIAnalysis should have relationship
    assert hasattr(AIAnalysis, 'finding')
    
    # DetectionRule should have relationship
    assert hasattr(DetectionRule, 'detections')
    
    # User should have relationship
    assert hasattr(User, 'audit_logs')
    
    # AuditLog should have relationship
    assert hasattr(AuditLog, 'user')
