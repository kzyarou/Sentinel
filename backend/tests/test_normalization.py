import pytest
from datetime import datetime
from app.services.normalization import EventNormalizer
from app.schemas.event import EventCreate


class TestEventNormalizer:
    """Test event normalization logic."""
    
    def test_normalize_ssh_event(self):
        """Test normalization of SSH event."""
        ssh_event = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "ip_address": "192.168.1.1",
            "port": 22,
            "protocol": "ssh2",
            "auth_method": "password",
            "host": "server1.example.com",
            "user": "admin"
        }
        
        normalized = EventNormalizer.normalize_event(ssh_event)
        
        assert isinstance(normalized, EventCreate)
        assert normalized.event_type == "ssh_login"
        assert normalized.source == "ssh"
        assert normalized.host == "server1.example.com"
        assert normalized.user == "admin"
        assert normalized.normalized_data is not None
        assert "ip_address" in normalized.normalized_data
        assert normalized.raw_data is not None
    
    def test_normalize_windows_event(self):
        """Test normalization of Windows event."""
        windows_event = {
            "source": "windows_logs",
            "timestamp": "2024-01-01T00:00:00Z",
            "event_id": 4624,
            "process_id": 1234,
            "process_name": "lsass.exe",
            "logon_type": 2,
            "host": "WIN-SERVER01",
            "user": "DOMAIN\\admin"
        }
        
        normalized = EventNormalizer.normalize_event(windows_event)
        
        assert isinstance(normalized, EventCreate)
        assert normalized.source == "windows_logs"
        assert normalized.host == "WIN-SERVER01"
        assert normalized.normalized_data is not None
        assert "windows_event_id" in normalized.normalized_data
        assert normalized.raw_data is not None
    
    def test_normalize_syslog_event(self):
        """Test normalization of syslog event."""
        syslog_event = {
            "source": "syslog",
            "timestamp": "2024-01-01T00:00:00Z",
            "priority": 6,
            "facility": 3,
            "program": "ssh",
            "pid": 12345,
            "host": "server1.example.com"
        }
        
        normalized = EventNormalizer.normalize_event(syslog_event)
        
        assert isinstance(normalized, EventCreate)
        assert normalized.source == "syslog"
        assert normalized.host == "server1.example.com"
        assert normalized.normalized_data is not None
        assert "priority" in normalized.normalized_data
        assert normalized.raw_data is not None
    
    def test_normalize_generic_event(self):
        """Test normalization of generic/unknown event."""
        generic_event = {
            "source": "unknown_source",
            "timestamp": "2024-01-01T00:00:00Z",
            "custom_field": "custom_value",
            "another_field": 123
        }
        
        normalized = EventNormalizer.normalize_event(generic_event)
        
        assert isinstance(normalized, EventCreate)
        assert normalized.source == "unknown_source"
        assert normalized.normalized_data is not None
        assert "custom_field" in normalized.normalized_data
        assert normalized.raw_data is not None
    
    def test_normalize_event_with_custom_source(self):
        """Test normalization with custom source parameter."""
        event_data = {
            "timestamp": "2024-01-01T00:00:00Z",
            "custom_field": "value"
        }
        
        normalized = EventNormalizer.normalize_event(event_data, source="custom_source")
        
        assert normalized.source == "custom_source"
    
    def test_normalize_event_type_derivation_ssh(self):
        """Test event type derivation for SSH events."""
        ssh_login_event = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "login": "success"
        }
        
        normalized = EventNormalizer.normalize_event(ssh_login_event)
        
        assert "login" in normalized.event_type.lower()
    
    def test_normalize_event_type_derivation_windows(self):
        """Test event type derivation for Windows events."""
        windows_login_event = {
            "source": "windows_logs",
            "timestamp": "2024-01-01T00:00:00Z",
            "login": "user logged in"
        }
        
        normalized = EventNormalizer.normalize_event(windows_login_event)
        
        assert "login" in normalized.event_type.lower()
    
    def test_normalize_host_normalization(self):
        """Test hostname normalization."""
        event_with_host = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "hostname": "server1.example.com"
        }
        
        normalized = EventNormalizer.normalize_event(event_with_host)
        
        assert normalized.host == "server1.example.com"
    
    def test_normalize_host_from_computer_field(self):
        """Test hostname extraction from computer field."""
        event_with_computer = {
            "source": "windows_logs",
            "timestamp": "2024-01-01T00:00:00Z",
            "computer": "WIN-SERVER01"
        }
        
        normalized = EventNormalizer.normalize_event(event_with_computer)
        
        assert normalized.host == "WIN-SERVER01"
    
    def test_normalize_user_normalization(self):
        """Test username normalization."""
        event_with_user = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "username": "admin"
        }
        
        normalized = EventNormalizer.normalize_event(event_with_user)
        
        assert normalized.user == "admin"
    
    def test_normalize_user_from_account_field(self):
        """Test username extraction from account field."""
        event_with_account = {
            "source": "windows_logs",
            "timestamp": "2024-01-01T00:00:00Z",
            "account": "DOMAIN\\admin"
        }
        
        normalized = EventNormalizer.normalize_event(event_with_account)
        
        assert normalized.user == "DOMAIN\\admin"
    
    def test_normalize_null_host_user(self):
        """Test normalization with null host and user."""
        minimal_event = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        normalized = EventNormalizer.normalize_event(minimal_event)
        
        assert normalized.host is None
        assert normalized.user is None
    
    def test_normalize_raw_data_preservation(self):
        """Test that raw data is preserved as JSON."""
        original_event = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "custom_field": "custom_value",
            "number_field": 123
        }
        
        normalized = EventNormalizer.normalize_event(original_event)
        
        assert normalized.raw_data is not None
        assert "custom_field" in normalized.raw_data
        assert "number_field" in normalized.raw_data
    
    def test_normalize_event_type_max_length(self):
        """Test that event type is truncated to max length."""
        long_type_event = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "event_type": "x" * 200  # Exceeds 100 limit
        }
        
        normalized = EventNormalizer.normalize_event(long_type_event)
        
        assert len(normalized.event_type) <= 100
    
    def test_normalize_host_max_length(self):
        """Test that hostname is truncated to max length."""
        long_host_event = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "x" * 300  # Exceeds 255 limit
        }
        
        normalized = EventNormalizer.normalize_event(long_host_event)
        
        assert len(normalized.host) <= 255
    
    def test_normalize_user_max_length(self):
        """Test that username is truncated to max length."""
        long_user_event = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "user": "x" * 300  # Exceeds 255 limit
        }
        
        normalized = EventNormalizer.normalize_event(long_user_event)
        
        assert len(normalized.user) <= 255
    
    def test_normalize_ssh_specific_fields(self):
        """Test SSH-specific field extraction."""
        ssh_event = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "ip_address": "192.168.1.1",
            "port": 22,
            "protocol": "ssh2",
            "auth_method": "publickey"
        }
        
        normalized = EventNormalizer.normalize_event(ssh_event)
        
        assert normalized.normalized_data["ip_address"] == "192.168.1.1"
        assert normalized.normalized_data["port"] == 22
        assert normalized.normalized_data["protocol"] == "ssh2"
        assert normalized.normalized_data["auth_method"] == "publickey"
    
    def test_normalize_windows_specific_fields(self):
        """Test Windows-specific field extraction."""
        windows_event = {
            "source": "windows_logs",
            "timestamp": "2024-01-01T00:00:00Z",
            "event_id": 4624,
            "process_id": 1234,
            "process_name": "svchost.exe",
            "logon_type": 3
        }
        
        normalized = EventNormalizer.normalize_event(windows_event)
        
        assert normalized.normalized_data["windows_event_id"] == 4624
        assert normalized.normalized_data["process_id"] == 1234
        assert normalized.normalized_data["process_name"] == "svchost.exe"
        assert normalized.normalized_data["logon_type"] == 3
    
    def test_normalize_syslog_specific_fields(self):
        """Test syslog-specific field extraction."""
        syslog_event = {
            "source": "syslog",
            "timestamp": "2024-01-01T00:00:00Z",
            "priority": 6,
            "facility": 3,
            "program": "nginx",
            "pid": 12345
        }
        
        normalized = EventNormalizer.normalize_event(syslog_event)
        
        assert normalized.normalized_data["priority"] == 6
        assert normalized.normalized_data["facility"] == 3
        assert normalized.normalized_data["program"] == "nginx"
        assert normalized.normalized_data["pid"] == 12345
    
    def test_normalize_preserves_source_specific_info(self):
        """Test that important source-specific information is preserved."""
        complex_event = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "ip_address": "192.168.1.1",
            "port": 22,
            "custom_metadata": {
                "session_id": "abc123",
                "client_version": "7.9"
            }
        }
        
        normalized = EventNormalizer.normalize_event(complex_event)
        
        # Source-specific fields should be in normalized_data
        assert "ip_address" in normalized.normalized_data
        # Custom metadata should be preserved in raw_data
        assert "custom_metadata" in normalized.raw_data
    
    def test_normalize_unknown_source(self):
        """Test normalization of unknown source."""
        unknown_event = {
            "source": "totally_unknown_source",
            "timestamp": "2024-01-01T00:00:00Z",
            "field1": "value1",
            "field2": "value2"
        }
        
        normalized = EventNormalizer.normalize_event(unknown_event)
        
        assert normalized.source == "totally_unknown_source"
        assert normalized.event_type == "unknown"
        assert "field1" in normalized.normalized_data
        assert "field2" in normalized.normalized_data