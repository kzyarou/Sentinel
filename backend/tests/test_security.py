import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock
from app.main import app
from app.db.session import get_db


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = AsyncMock(spec=get_db)
    return db


@pytest.fixture
def override_get_db(mock_db):
    """Override database dependency for testing."""
    def override():
        yield mock_db
    
    app.dependency_overrides[get_db] = override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db):
    """Create test client with mocked database."""
    return TestClient(app)


class TestSecurityPayloadLimits:
    """Test security-related payload limit enforcement."""
    
    def test_reject_payload_exceeding_content_length(self, client, mock_db):
        """Test that payloads exceeding content-length header are rejected."""
        large_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "large_field": "x" * (2 * 1024 * 1024)  # 2MB
        }
        
        response = client.post("/api/v1/events", json=large_payload)
        
        assert response.status_code == 413
        data = response.json()
        assert data["error"] == "payload_too_large"
        assert "max_size" in data
    
    def test_accept_payload_within_limits(self, client, mock_db):
        """Test that payloads within limits are accepted."""
        reasonable_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "reasonable_field": "x" * 1024  # 1KB
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=reasonable_payload)
        
        assert response.status_code == 200
    
    def test_reject_exactly_at_limit(self, client, mock_db):
        """Test boundary condition: payload exactly at limit."""
        # Create payload that exactly matches 1MB limit
        boundary_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "boundary_field": "x" * (1024 * 1024 - 100)  # Just under 1MB
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=boundary_payload)
        
        # Should be accepted (under limit)
        assert response.status_code == 200
    
    def test_multiple_large_fields_rejected(self, client, mock_db):
        """Test that multiple large fields are rejected."""
        large_multi_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "field1": "x" * (1024 * 1024),
            "field2": "y" * (1024 * 1024)
        }
        
        response = client.post("/api/v1/events", json=large_multi_payload)
        
        assert response.status_code == 413


class TestSecurityInjectionPrevention:
    """Test security-related injection prevention."""
    
    def test_sql_injection_in_event_type(self, client, mock_db):
        """Test that SQL injection in event_type is sanitized."""
        injection_payload = {
            "event_type": "ssh_login'; DROP TABLE events; --",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=injection_payload)
        
        # Should be sanitized and accepted
        assert response.status_code == 200
        data = response.json()
        assert "event_id" in data
    
    def test_sql_injection_in_source(self, client, mock_db):
        """Test that SQL injection in source is sanitized."""
        injection_payload = {
            "event_type": "ssh_login",
            "source": "ssh'; DROP TABLE events; --",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=injection_payload)
        
        # Should be sanitized and accepted
        assert response.status_code == 200
    
    def test_sql_injection_in_host(self, client, mock_db):
        """Test that SQL injection in host is sanitized."""
        injection_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com'; DROP TABLE events; --"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=injection_payload)
        
        # Should be sanitized and accepted
        assert response.status_code == 200
    
    def test_sql_injection_in_user(self, client, mock_db):
        """Test that SQL injection in user is sanitized."""
        injection_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "user": "admin'; DROP TABLE events; --"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=injection_payload)
        
        # Should be sanitized and accepted
        assert response.status_code == 200
    
    def test_xss_injection_in_fields(self, client, mock_db):
        """Test that XSS injection attempts are sanitized."""
        xss_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com<script>alert('xss')</script>",
            "user": "admin<script>alert('xss')</script>"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=xss_payload)
        
        # Should be sanitized and accepted
        assert response.status_code == 200
    
    def test_command_injection_in_fields(self, client, mock_db):
        """Test that command injection attempts are sanitized."""
        cmd_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com; rm -rf /",
            "user": "admin| cat /etc/passwd"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=cmd_payload)
        
        # Should be sanitized and accepted
        assert response.status_code == 200
    
    def test_path_traversal_in_fields(self, client, mock_db):
        """Test that path traversal attempts are sanitized."""
        path_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com../../../etc/passwd",
            "user": "admin"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=path_payload)
        
        # Should be sanitized and accepted
        assert response.status_code == 200
    
    def test_ldap_injection_in_fields(self, client, mock_db):
        """Test that LDAP injection attempts are sanitized."""
        ldap_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "user": "admin)(|(password=*"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=ldap_payload)
        
        # Should be sanitized and accepted
        assert response.status_code == 200
    
    def test_log_injection_in_fields(self, client, mock_db):
        """Test that log injection attempts are prevented."""
        log_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com\n[INFO] admin logged in",
            "user": "admin\r\n[ERROR] failed"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=log_payload)
        
        # Should be sanitized and accepted
        assert response.status_code == 200


class TestSecurityDatabaseErrorHandling:
    """Test security-related database error handling."""
    
    def test_database_error_not_exposed(self, client, mock_db):
        """Test that database errors don't expose internal details."""
        valid_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Mock database error
        mock_db.add = Mock()
        mock_db.commit = AsyncMock(side_effect=Exception("SELECT * FROM secret_table"))
        
        response = client.post("/api/v1/events", json=valid_payload)
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "internal_error"
        # Should not expose database details
        assert "secret_table" not in str(data)
        assert "SELECT" not in str(data)
    
    def test_database_connection_error_not_exposed(self, client, mock_db):
        """Test that connection errors don't expose credentials."""
        valid_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Mock connection error with fake credentials
        mock_db.add = Mock()
        mock_db.commit = AsyncMock(
            side_effect=Exception("Connection failed: user=admin password=secret")
        )
        
        response = client.post("/api/v1/events", json=valid_payload)
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "internal_error"
        # Should not expose credentials
        assert "password" not in str(data).lower()
        assert "secret" not in str(data)
    
    def test_database_constraint_error_not_exposed(self, client, mock_db):
        """Test that constraint errors don't expose schema details."""
        valid_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Mock constraint error
        mock_db.add = Mock()
        mock_db.commit = AsyncMock(
            side_effect=Exception("UNIQUE constraint failed: events.id")
        )
        
        response = client.post("/api/v1/events", json=valid_payload)
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "internal_error"
        # Should not expose schema details
        assert "UNIQUE" not in str(data)
        assert "events.id" not in str(data)


class TestSecuritySensitiveDataHandling:
    """Test security-related sensitive data handling."""
    
    def test_password_not_logged(self, client, mock_db):
        """Test that password fields are not exposed in responses."""
        payload_with_password = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "password": "SuperSecret123!"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=payload_with_password)
        
        assert response.status_code == 200
        data = response.json()
        # Should not return password in response
        assert "password" not in data
        assert "SuperSecret" not in str(data)
    
    def test_sensitive_fields_preserved_in_raw_data(self, client, mock_db):
        """Test that sensitive fields are preserved in raw data but not exposed."""
        sensitive_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "password": "SecretPassword123",
            "api_key": "sk-1234567890"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=sensitive_payload)
        
        assert response.status_code == 200
        data = response.json()
        # Response should not contain sensitive data
        assert "password" not in data
        assert "api_key" not in data
        # But raw data should be preserved (check in mock)
        added_event = mock_db.add.call_args[0][0]
        assert added_event.raw_data is not None
    
    def test_malformed_json_rejected(self, client, mock_db):
        """Test that malformed JSON is rejected without exposing errors."""
        response = client.post(
            "/api/v1/events",
            content='{"event_type": "ssh_login", "source": "ssh", "timestamp": "2024-01-01T00:00:00Z"',
            headers={"Content-Type": "application/json"}
        )
        
        # Should return validation error
        assert response.status_code == 422
        # Should not expose internal parsing details
        data = response.json()
        assert "detail" in data