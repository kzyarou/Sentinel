import pytest
from datetime import datetime
from app.services.validation import EventValidator, EventValidationError


class TestEventValidator:
    """Test event validation logic."""
    
    def test_validate_required_fields_success(self):
        """Test validation with all required fields present."""
        valid_data = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Should not raise exception
        EventValidator.validate_required_fields(valid_data)
    
    def test_validate_required_fields_missing_type(self):
        """Test validation fails when event_type is missing."""
        invalid_data = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with pytest.raises(EventValidationError) as exc_info:
            EventValidator.validate_required_fields(invalid_data)
        
        assert "event_type" in str(exc_info.value).lower()
    
    def test_validate_required_fields_missing_source(self):
        """Test validation fails when source is missing."""
        invalid_data = {
            "event_type": "ssh_login",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with pytest.raises(EventValidationError) as exc_info:
            EventValidator.validate_required_fields(invalid_data)
        
        assert "source" in str(exc_info.value).lower()
    
    def test_validate_required_fields_missing_timestamp(self):
        """Test validation fails when timestamp is missing."""
        invalid_data = {
            "event_type": "ssh_login",
            "source": "ssh"
        }
        
        with pytest.raises(EventValidationError) as exc_info:
            EventValidator.validate_required_fields(invalid_data)
        
        assert "timestamp" in str(exc_info.value).lower()
    
    def test_validate_field_lengths_success(self):
        """Test field length validation with valid lengths."""
        valid_data = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com",
            "user": "admin"
        }
        
        # Should not raise exception
        EventValidator.validate_field_lengths(valid_data)
    
    def test_validate_field_lengths_exceeds_max(self):
        """Test validation fails when field exceeds max length."""
        invalid_data = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "x" * 300  # Exceeds 255 limit
        }
        
        with pytest.raises(EventValidationError) as exc_info:
            EventValidator.validate_field_lengths(invalid_data)
        
        assert "host" in str(exc_info.value).lower()
    
    def test_validate_timestamp_valid(self):
        """Test validation with valid timestamp."""
        valid_timestamp = "2024-01-01T00:00:00Z"
        
        result = EventValidator.validate_timestamp(valid_timestamp)
        assert isinstance(result, datetime)
    
    def test_validate_timestamp_invalid_format(self):
        """Test validation fails with invalid timestamp format."""
        invalid_timestamp = "invalid-timestamp"
        
        with pytest.raises(EventValidationError):
            EventValidator.validate_timestamp(invalid_timestamp)
    
    def test_validate_timestamp_future(self):
        """Test validation fails with future timestamp."""
        future_timestamp = "2030-01-01T00:00:00Z"
        
        with pytest.raises(EventValidationError):
            EventValidator.validate_timestamp(future_timestamp)
    
    def test_validate_payload_size_valid(self):
        """Test payload size validation with valid size."""
        valid_payload = '{"event_type": "ssh_login"}'
        
        # Should not raise exception
        EventValidator.validate_payload_size(valid_payload)
    
    def test_validate_payload_size_exceeds_limit(self):
        """Test validation fails when payload exceeds limit."""
        # Create a payload that exceeds 1MB
        large_payload = '{"data": "' + 'x' * (2 * 1024 * 1024) + '"}'
        
        with pytest.raises(EventValidationError):
            EventValidator.validate_payload_size(large_payload)
    
    def test_sanitize_input_success(self):
        """Test input sanitization removes dangerous characters."""
        dirty_input = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com'; DROP TABLE events; --",
            "user": "admin<script>alert('xss')</script>"
        }
        
        sanitized = EventValidator.sanitize_input(dirty_input)
        
        # Should remove dangerous characters
        assert ";" not in sanitized.get("host", "")
        assert "<script>" not in sanitized.get("user", "")
    
    def test_sanitize_input_preserves_valid_data(self):
        """Test sanitization preserves valid data."""
        valid_input = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com",
            "user": "admin"
        }
        
        sanitized = EventValidator.sanitize_input(valid_input)
        
        # Should preserve valid data
        assert sanitized["event_type"] == "ssh_login"
        assert sanitized["source"] == "ssh"
        assert sanitized["host"] == "server1.example.com"
        assert sanitized["user"] == "admin"
    
    def test_validate_event_data_success(self):
        """Test schema validation with valid event data."""
        valid_data = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = EventValidator.validate_event_data(valid_data)
        
        assert result is not None
        assert result.event_type == "ssh_login"
        assert result.source == "ssh"
    
    def test_validate_event_data_invalid_schema(self):
        """Test schema validation fails with invalid data."""
        invalid_data = {
            "event_type": 123,  # Should be string
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with pytest.raises(EventValidationError):
            EventValidator.validate_event_data(invalid_data)
    
    def test_validate_event_data_missing_optional_fields(self):
        """Test schema validation succeeds with optional fields missing."""
        minimal_data = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = EventValidator.validate_event_data(minimal_data)
        
        assert result is not None
        assert result.host is None
        assert result.user is None
    
    def test_validate_supported_source(self):
        """Test source validation with supported source."""
        supported_source = "ssh"
        
        # Should not raise exception
        EventValidator.validate_supported_source(supported_source)
    
    def test_validate_unsupported_source(self):
        """Test source validation with unsupported source."""
        unsupported_source = "unsupported_source"
        
        # Should still accept but log warning
        EventValidator.validate_supported_source(unsupported_source)
    
    def test_validate_timestamp_before_allowed(self):
        """Test validation fails with timestamp before allowed range."""
        old_timestamp = "2000-01-01T00:00:00Z"
        
        with pytest.raises(EventValidationError):
            EventValidator.validate_timestamp(old_timestamp)
    
    def test_validate_field_lengths_null_values(self):
        """Test field length validation handles null values."""
        data_with_nulls = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": None,
            "user": None
        }
        
        # Should not raise exception for null values
        EventValidator.validate_field_lengths(data_with_nulls)
    
    def test_validate_empty_string(self):
        """Test validation handles empty strings."""
        data_with_empty = {
            "event_type": "",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with pytest.raises(EventValidationError):
            EventValidator.validate_required_fields(data_with_empty)