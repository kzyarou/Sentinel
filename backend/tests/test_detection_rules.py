import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.detection_rule import DetectionRule
from app.detection.rule_engine import RuleEvaluator, RuleEvaluationResult
from app.schemas.detection_rule import DetectionRuleCreate


class TestRule001AuthBruteforce:
    """Test Rule 001: Repeated Authentication Failures."""
    
    @pytest.fixture
    def auth_bruteforce_rule(self):
        """Create the AUTH-BRUTEFORCE rule for testing."""
        return DetectionRule(
            id="rule-001",
            name="AUTH-BRUTEFORCE",
            description="Detect repeated authentication failures",
            category="authentication",
            severity="HIGH",
            version="1",
            enabled=True,
            rule_definition={
                "failure_threshold": 5,
                "time_window_minutes": 5,
                "track_by": "user"
            }
        )
    
    @pytest.fixture
    def auth_failure_event(self):
        """Create an authentication failure event."""
        return Event(
            id="event-001",
            event_type="auth_failure",
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            host="server1.example.com",
            normalized_data={
                "user": "testuser",
                "source_ip": "192.168.1.100",
                "metadata": {
                    "recent_failures": 6  # Above threshold
                }
            }
        )
    
    def test_positive_case_threshold_exceeded(self, auth_failure_event, auth_bruteforce_rule):
        """Test that rule triggers when failure threshold is exceeded."""
        result = RuleEvaluator.evaluate(auth_failure_event, auth_bruteforce_rule)
        
        assert result.matched is True
        assert result.rule == auth_bruteforce_rule
        assert result.severity == "HIGH"
        assert result.confidence > 0.5
        assert len(result.evidence) > 0
        assert any(e["type"] == "auth_failure_count" for e in result.evidence)
    
    def test_positive_case_exactly_at_threshold(self, auth_bruteforce_rule):
        """Test that rule triggers when exactly at threshold."""
        event = Event(
            id="event-002",
            event_type="auth_failure",
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            normalized_data={
                "user": "testuser",
                "metadata": {
                    "recent_failures": 5  # Exactly at threshold
                }
            }
        )
        
        result = RuleEvaluator.evaluate(event, auth_bruteforce_rule)
        
        assert result.matched is True
        assert result.confidence >= 0.5
    
    def test_negative_case_below_threshold(self, auth_bruteforce_rule):
        """Test that rule does not trigger when below threshold."""
        event = Event(
            id="event-003",
            event_type="auth_failure",
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            normalized_data={
                "user": "testuser",
                "metadata": {
                    "recent_failures": 3  # Below threshold
                }
            }
        )
        
        result = RuleEvaluator.evaluate(event, auth_bruteforce_rule)
        
        assert result.matched is False
        assert result.error is None
    
    def test_negative_case_wrong_event_type(self, auth_bruteforce_rule):
        """Test that rule does not trigger for non-auth events."""
        event = Event(
            id="event-004",
            event_type="auth_success",  # Wrong event type
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            normalized_data={
                "user": "testuser",
                "metadata": {
                    "recent_failures": 10
                }
            }
        )
        
        result = RuleEvaluator.evaluate(event, auth_bruteforce_rule)
        
        assert result.matched is False
    
    def test_boundary_case_zero_failures(self, auth_bruteforce_rule):
        """Test boundary case with zero failures."""
        event = Event(
            id="event-005",
            event_type="auth_failure",
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            normalized_data={
                "user": "testuser",
                "metadata": {
                    "recent_failures": 0
                }
            }
        )
        
        result = RuleEvaluator.evaluate(event, auth_bruteforce_rule)
        
        assert result.matched is False
    
    def test_boundary_case_very_high_failures(self, auth_bruteforce_rule):
        """Test boundary case with very high failure count."""
        event = Event(
            id="event-006",
            event_type="auth_failure",
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            normalized_data={
                "user": "testuser",
                "metadata": {
                    "recent_failures": 100  # Very high
                }
            }
        )
        
        result = RuleEvaluator.evaluate(event, auth_bruteforce_rule)
        
        assert result.matched is True
        assert result.confidence == 1.0  # Should cap at 1.0
    
    def test_malformed_input_missing_tracking_field(self, auth_bruteforce_rule):
        """Test handling of missing tracking field."""
        event = Event(
            id="event-007",
            event_type="auth_failure",
            source="ssh",
            timestamp=datetime.utcnow(),
            normalized_data={
                # Missing 'user' field
                "metadata": {
                    "recent_failures": 10
                }
            }
        )
        
        result = RuleEvaluator.evaluate(event, auth_bruteforce_rule)
        
        assert result.matched is False
        assert result.error is not None
        assert "tracking field" in result.error.lower()
    
    def test_malformed_input_missing_metadata(self, auth_bruteforce_rule):
        """Test handling of missing metadata."""
        event = Event(
            id="event-008",
            event_type="auth_failure",
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            normalized_data={
                "user": "testuser"
                # Missing metadata
            }
        )
        
        result = RuleEvaluator.evaluate(event, auth_bruteforce_rule)
        
        # Should handle gracefully (treat as 0 failures)
        assert result.matched is False
    
    def test_confidence_calculation(self, auth_bruteforce_rule):
        """Test that confidence increases with failure count."""
        event_low = Event(
            id="event-009",
            event_type="auth_failure",
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            normalized_data={
                "user": "testuser",
                "metadata": {"recent_failures": 6}
            }
        )
        
        event_high = Event(
            id="event-010",
            event_type="auth_failure",
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            normalized_data={
                "user": "testuser",
                "metadata": {"recent_failures": 15}
            }
        )
        
        result_low = RuleEvaluator.evaluate(event_low, auth_bruteforce_rule)
        result_high = RuleEvaluator.evaluate(event_high, auth_bruteforce_rule)
        
        assert result_high.confidence > result_low.confidence
    
    def test_evidence_content(self, auth_failure_event, auth_bruteforce_rule):
        """Test that evidence contains expected information."""
        result = RuleEvaluator.evaluate(auth_failure_event, auth_bruteforce_rule)
        
        assert result.matched is True
        
        # Check for specific evidence types
        evidence_types = [e["type"] for e in result.evidence]
        assert "auth_failure_count" in evidence_types
        assert "event_reference" in evidence_types
        
        # Check evidence content
        failure_evidence = next(e for e in result.evidence if e["type"] == "auth_failure_count")
        assert failure_evidence["tracking_value"] == "testuser"
        assert failure_evidence["threshold"] == 5


class TestRule002PrivilegedAction:
    """Test Rule 002: Suspicious Privileged Action."""
    
    @pytest.fixture
    def privileged_action_rule(self):
        """Create the PRIVILEGED-ACTION rule for testing."""
        return DetectionRule(
            id="rule-002",
            name="PRIVILEGED-ACTION",
            description="Detect suspicious privileged actions",
            category="privilege_escalation",
            severity="HIGH",
            version="1",
            enabled=True,
            rule_definition={
                "privileged_actions": ["sudo_command", "user_modification"],
                "require_elevation": True,
                "suspicious_conditions": {}
            }
        )
    
    @pytest.fixture
    def privileged_event(self):
        """Create a privileged action event."""
        return Event(
            id="event-011",
            event_type="privileged_action",
            source="system",
            timestamp=datetime.utcnow(),
            user="admin",
            normalized_data={
                "action": "sudo_command",
                "elevated": True,
                "user": "admin",
                "command": "useradd -m attacker"
            }
        )
    
    def test_positive_case_privileged_action_detected(self, privileged_event, privileged_action_rule):
        """Test that rule triggers for elevated privileged actions."""
        result = RuleEvaluator.evaluate(privileged_event, privileged_action_rule)
        
        assert result.matched is True
        assert result.severity == "HIGH"
        assert result.confidence >= 0.7
        assert len(result.evidence) > 0
    
    def test_positive_case_specific_action_in_list(self, privileged_action_rule):
        """Test that rule triggers for actions in privileged list."""
        event = Event(
            id="event-012",
            event_type="privileged_action",
            source="system",
            timestamp=datetime.utcnow(),
            normalized_data={
                "action": "user_modification",  # In list
                "elevated": True
            }
        )
        
        result = RuleEvaluator.evaluate(event, privileged_action_rule)
        
        assert result.matched is True
    
    def test_negative_case_action_not_in_list(self, privileged_action_rule):
        """Test that rule does not trigger for non-privileged actions."""
        event = Event(
            id="event-013",
            event_type="privileged_action",
            source="system",
            timestamp=datetime.utcnow(),
            normalized_data={
                "action": "file_read",  # Not in privileged list
                "elevated": True
            }
        )
        
        result = RuleEvaluator.evaluate(event, privileged_action_rule)
        
        assert result.matched is False
    
    def test_negative_case_not_elevated(self, privileged_action_rule):
        """Test that rule does not trigger when elevation is required but not present."""
        event = Event(
            id="event-014",
            event_type="privileged_action",
            source="system",
            timestamp=datetime.utcnow(),
            normalized_data={
                "action": "sudo_command",
                "elevated": False  # Not elevated
            }
        )
        
        result = RuleEvaluator.evaluate(event, privileged_action_rule)
        
        assert result.matched is False
    
    def test_negative_case_wrong_event_type(self, privileged_action_rule):
        """Test that rule does not trigger for non-privileged events."""
        event = Event(
            id="event-015",
            event_type="normal_action",  # Wrong event type
            source="system",
            timestamp=datetime.utcnow(),
            normalized_data={
                "action": "sudo_command",
                "elevated": True
            }
        )
        
        result = RuleEvaluator.evaluate(event, privileged_action_rule)
        
        assert result.matched is False
    
    def test_boundary_case_no_elevation_requirement(self):
        """Test when elevation requirement is disabled."""
        rule = DetectionRule(
            id="rule-002b",
            name="PRIVILEGED-ACTION",
            description="Detect suspicious privileged actions",
            category="privilege_escalation",
            severity="HIGH",
            version="1",
            enabled=True,
            rule_definition={
                "privileged_actions": ["sudo_command"],
                "require_elevation": False,  # Disabled
                "suspicious_conditions": {}
            }
        )
        
        event = Event(
            id="event-016",
            event_type="privileged_action",
            source="system",
            timestamp=datetime.utcnow(),
            normalized_data={
                "action": "sudo_command",
                "elevated": False  # Not elevated but not required
            }
        )
        
        result = RuleEvaluator.evaluate(event, rule)
        
        assert result.matched is True
    
    def test_malformed_input_missing_action(self, privileged_action_rule):
        """Test handling of missing action field."""
        event = Event(
            id="event-017",
            event_type="privileged_action",
            source="system",
            timestamp=datetime.utcnow(),
            normalized_data={
                "elevated": True
                # Missing action
            }
        )
        
        result = RuleEvaluator.evaluate(event, privileged_action_rule)
        
        assert result.matched is False
    
    def test_suspicious_conditions_match(self):
        """Test that suspicious conditions increase confidence."""
        rule = DetectionRule(
            id="rule-002c",
            name="PRIVILEGED-ACTION",
            description="Detect suspicious privileged actions",
            category="privilege_escalation",
            severity="HIGH",
            version="1",
            enabled=True,
            rule_definition={
                "privileged_actions": ["sudo_command"],
                "require_elevation": True,
                "suspicious_conditions": {
                    "outside_business_hours": True
                }
            }
        )
        
        event = Event(
            id="event-018",
            event_type="privileged_action",
            source="system",
            timestamp=datetime.utcnow(),
            normalized_data={
                "action": "sudo_command",
                "elevated": True,
                "outside_business_hours": True  # Matches condition
            }
        )
        
        result = RuleEvaluator.evaluate(event, rule)
        
        assert result.matched is True
        assert result.confidence > 0.7  # Should be higher than base


class TestRule003UnusualAuthSource:
    """Test Rule 003: Unusual Authentication Source."""
    
    @pytest.fixture
    def unusual_auth_rule(self):
        """Create the UNUSUAL-AUTH-SOURCE rule for testing."""
        return DetectionRule(
            id="rule-003",
            name="UNUSUAL-AUTH-SOURCE",
            description="Detect unusual authentication sources",
            category="authentication",
            severity="MEDIUM",
            version="1",
            enabled=True,
            rule_definition={
                "trusted_sources": ["192.168.1.0/24", "10.0.0.0/8"],
                "blocked_sources": ["0.0.0.0/8"],
                "check_geoip": False,
                "unusual_countries": []
            }
        )
    
    @pytest.fixture
    def auth_event(self):
        """Create an authentication event."""
        return Event(
            id="event-019",
            event_type="auth_success",
            source="ssh",
            timestamp=datetime.utcnow(),
            user="testuser",
            normalized_data={
                "user": "testuser",
                "source_ip": "192.168.1.100"
            }
        )
    
    def test_positive_case_blocked_source(self, unusual_auth_rule):
        """Test that rule triggers for blocked sources."""
        event = Event(
            id="event-020",
            event_type="auth_success",
            source="ssh",
            timestamp=datetime.utcnow(),
            normalized_data={
                "source_ip": "0.0.0.1"  # In blocked range
            }
        )
        
        result = RuleEvaluator.evaluate(event, unusual_auth_rule)
        
        assert result.matched is True
        assert result.confidence == 1.0  # High confidence for blocked
        assert len(result.evidence) > 0
    
    def test_positive_case_untrusted_source(self, unusual_auth_rule):
        """Test that rule triggers for untrusted sources when trusted list is specified."""
        event = Event(
            id="event-021",
            event_type="auth_success",
            source="ssh",
            timestamp=datetime.utcnow(),
            normalized_data={
                "source_ip": "8.8.8.8"  # Not in trusted list
            }
        )
        
        result = RuleEvaluator.evaluate(event, unusual_auth_rule)
        
        assert result.matched is True
        assert result.confidence >= 0.7
    
    def test_negative_case_trusted_source(self, auth_event, unusual_auth_rule):
        """Test that rule does not trigger for trusted sources."""
        result = RuleEvaluator.evaluate(auth_event, unusual_auth_rule)
        
        assert result.matched is False
    
    def test_negative_case_non_auth_event(self, unusual_auth_rule):
        """Test that rule does not trigger for non-auth events."""
        event = Event(
            id="event-022",
            event_type="file_access",  # Wrong event type
            source="system",
            timestamp=datetime.utcnow(),
            normalized_data={
                "source_ip": "0.0.0.1"
            }
        )
        
        result = RuleEvaluator.evaluate(event, unusual_auth_rule)
        
        assert result.matched is False
    
    def test_boundary_case_no_trusted_list(self):
        """Test when no trusted list is specified."""
        rule = DetectionRule(
            id="rule-003b",
            name="UNUSUAL-AUTH-SOURCE",
            description="Detect unusual authentication sources",
            category="authentication",
            severity="MEDIUM",
            version="1",
            enabled=True,
            rule_definition={
                "trusted_sources": [],  # Empty list
                "blocked_sources": ["0.0.0.0/8"],
                "check_geoip": False,
                "unusual_countries": []
            }
        )
        
        event = Event(
            id="event-023",
            event_type="auth_success",
            source="ssh",
            timestamp=datetime.utcnow(),
            normalized_data={
                "source_ip": "8.8.8.8"
            }
        )
        
        result = RuleEvaluator.evaluate(event, rule)
        
        # Should not trigger since no trusted list and not blocked
        assert result.matched is False
    
    def test_malformed_input_missing_source_ip(self, unusual_auth_rule):
        """Test handling of missing source IP."""
        event = Event(
            id="event-024",
            event_type="auth_success",
            source="ssh",
            timestamp=datetime.utcnow(),
            normalized_data={
                "user": "testuser"
                # Missing source_ip
            }
        )
        
        result = RuleEvaluator.evaluate(event, unusual_auth_rule)
        
        assert result.matched is False
        assert result.error is not None
        assert "source ip" in result.error.lower()
    
    def test_geoip_check_enabled(self):
        """Test geographic location checking."""
        rule = DetectionRule(
            id="rule-003c",
            name="UNUSUAL-AUTH-SOURCE",
            description="Detect unusual authentication sources",
            category="authentication",
            severity="MEDIUM",
            version="1",
            enabled=True,
            rule_definition={
                "trusted_sources": [],
                "blocked_sources": [],
                "check_geoip": True,
                "unusual_countries": ["CN", "RU"]
            }
        )
        
        event = Event(
            id="event-025",
            event_type="auth_success",
            source="ssh",
            timestamp=datetime.utcnow(),
            normalized_data={
                "source_ip": "1.2.3.4",
                "country": "CN"  # Unusual country
            }
        )
        
        result = RuleEvaluator.evaluate(event, rule)
        
        assert result.matched is True
        assert result.confidence >= 0.8
        assert any(e["type"] == "unusual_geo_location" for e in result.evidence)
    
    def test_rule_version_preserved(self, auth_event, unusual_auth_rule):
        """Test that rule version is preserved in evaluation result."""
        result = RuleEvaluator.evaluate(auth_event, unusual_auth_rule)
        
        assert result.rule.version == "1"
        assert result.rule.name == "UNUSUAL-AUTH-SOURCE"