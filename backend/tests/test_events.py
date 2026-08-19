import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from app.main import app
from app.db.session import get_db
from app.schemas.event import EventCreate
from app.models.event import Event


# Mock database for testing
@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = AsyncMock(spec=AsyncSession)
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


class TestEventIngestion:
    """Test event ingestion endpoint."""
    
    def test_valid_event_ingestion(self, client, mock_db):
        """Test that a valid event is accepted and ingested."""
        # Mock the event creation
        mock_event = Event(
            id="test-event-id",
            event_type="ssh_login",
            source="ssh",
            timestamp=datetime.utcnow(),
            host="server1.example.com",
            user="admin",
            normalized_data={"ip_address": "192.168.1.1"},
            raw_data='{"ip_address": "192.168.1.1"}'
        )
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Set return value for refresh
        mock_db.refresh.return_value = None
        
        valid_event = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com",
            "user": "admin",
            "ip_address": "192.168.1.1"
        }
        
        response = client.post("/api/v1/events", json=valid_event)
        
        assert response.status_code == 200
        data = response.json()
        assert "event_id" in data
        assert data["status"] == "ingested"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_missing_required_field(self, client, mock_db):
        """Test that missing required fields are rejected."""
        invalid_event = {
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
            # Missing event_type
        }
        
        response = client.post("/api/v1/events", json=invalid_event)
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "validation_error"
        assert "message" in data
    
    def test_invalid_timestamp(self, client, mock_db):
        """Test that invalid timestamps are rejected."""
        invalid_event = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "invalid-timestamp",
            "host": "server1.example.com"
        }
        
        response = client.post("/api/v1/events", json=invalid_event)
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "validation_error"
    
    def test_invalid_data_type(self, client, mock_db):
        """Test that invalid data types are rejected."""
        invalid_event = {
            "event_type": 123,  # Should be string
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        response = client.post("/api/v1/events", json=invalid_event)
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "validation_error"
    
    def test_malformed_json(self, client, mock_db):
        """Test that malformed JSON is rejected."""
        response = client.post(
            "/api/v1/events",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_oversized_payload(self, client, mock_db):
        """Test that oversized payloads are rejected."""
        # Create a payload that exceeds 1MB
        large_payload = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "large_field": "x" * (2 * 1024 * 1024)  # 2MB string
        }
        
        response = client.post("/api/v1/events", json=large_payload)
        
        # Should be rejected by middleware
        assert response.status_code == 413
        data = response.json()
        assert data["error"] == "payload_too_large"
    
    def test_unsupported_event_type(self, client, mock_db):
        """Test that unsupported event types are normalized but accepted."""
        # Unknown event types should be normalized to 'unknown'
        unknown_event = {
            "event_type": "unsupported_type",
            "source": "unknown_source",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=unknown_event)
        
        # Should be accepted (normalized)
        assert response.status_code == 200
        data = response.json()
        assert "event_id" in data
    
    def test_injection_attempt_in_field(self, client, mock_db):
        """Test that injection attempts in fields are handled safely."""
        injection_event = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "host": "server1.example.com'; DROP TABLE events; --",
            "user": "admin"
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=injection_event)
        
        # Should be sanitized and accepted
        assert response.status_code == 200
        data = response.json()
        assert "event_id" in data
    
    def test_database_error_handling(self, client, mock_db):
        """Test that database errors are handled gracefully."""
        valid_event = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Mock database error
        mock_db.add = Mock()
        mock_db.commit = AsyncMock(side_effect=Exception("Database connection failed"))
        
        response = client.post("/api/v1/events", json=valid_event)
        
        # Should return 500 without exposing database details
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "internal_error"
        assert "Database connection failed" not in str(data)
    
    def test_raw_data_preservation(self, client, mock_db):
        """Test that raw event data is preserved."""
        raw_event = {
            "event_type": "ssh_login",
            "source": "ssh",
            "timestamp": "2024-01-01T00:00:00Z",
            "custom_field": "custom_value",
            "another_field": 123
        }
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        response = client.post("/api/v1/events", json=raw_event)
        
        assert response.status_code == 200
        # Verify that the event was created with preserved raw data
        mock_db.add.assert_called_once()
        added_event = mock_db.add.call_args[0][0]
        assert added_event.raw_data is not None


class TestEventRetrieval:
    """Test event retrieval endpoint."""
    
    def test_get_event_by_id(self, client, mock_db):
        """Test retrieving an event by ID."""
        event_id = "test-event-id"
        
        # Mock the event retrieval
        mock_event = Event(
            id=event_id,
            event_type="ssh_login",
            source="ssh",
            timestamp=datetime.utcnow(),
            host="server1.example.com",
            user="admin",
            normalized_data={"ip_address": "192.168.1.1"},
            raw_data='{"ip_address": "192.168.1.1"}'
        )
        
        # Mock the execute method
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_event
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        response = client.get(f"/api/v1/events/{event_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event_id
        assert data["event_type"] == "ssh_login"
    
    def test_get_nonexistent_event(self, client, mock_db):
        """Test retrieving a nonexistent event."""
        event_id = "nonexistent-event-id"
        
        # Mock the event retrieval returning None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        response = client.get(f"/api/v1/events/{event_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "not_found"
    
    def test_get_event_invalid_id(self, client, mock_db):
        """Test retrieving event with invalid ID."""
        invalid_id = "invalid-id-format"
        
        response = client.get(f"/api/v1/events/{invalid_id}")
        
        # Should return 404 or validation error
        assert response.status_code in [404, 400]