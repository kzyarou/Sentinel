import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from app.main import app
from app.db.session import get_db
from app.models.finding import Finding, FindingStatus
from app.models.detection import Detection
from app.schemas.finding import FindingCreate, FindingUpdate


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


@pytest.fixture
def mock_finding():
    """Create a mock finding."""
    return Finding(
        id="test-finding-id",
        title="Test Finding",
        description="Test description",
        severity="HIGH",
        confidence=85,
        status=FindingStatus.OPEN,
        detection_id="test-detection-id",
        finding_metadata={"rule_name": "TEST-RULE"},
        created_timestamp=datetime.utcnow(),
        updated_timestamp=datetime.utcnow()
    )


@pytest.fixture
def mock_detection():
    """Create a mock detection."""
    return Detection(
        id="test-detection-id",
        detection_rule_id="test-rule-id",
        event_id="test-event-id",
        detection_timestamp=datetime.utcnow(),
        severity="HIGH",
        confidence=85,
        rule_version="1",
        detection_metadata={"rule_name": "TEST-RULE"}
    )


class TestFindingCreation:
    """Test finding creation operations."""
    
    def test_create_finding_from_detection(self, mock_db, mock_detection):
        """Test that a finding can be created from a detection."""
        from app.services.finding_service import FindingService
        
        # Mock database operations
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        finding = FindingService.create_finding_from_detection(
            db=mock_db,
            detection=mock_detection
        )
        
        assert finding is not None
        assert finding.severity == mock_detection.severity
        assert finding.confidence == mock_detection.confidence
        assert finding.status == FindingStatus.OPEN
        assert finding.detection_id == mock_detection.id
        assert "TEST-RULE" in finding.title
    
    def test_create_finding_with_custom_title(self, mock_db, mock_detection):
        """Test finding creation with custom title."""
        from app.services.finding_service import FindingService
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        custom_title = "Custom Security Finding"
        finding = FindingService.create_finding_from_detection(
            db=mock_db,
            detection=mock_detection,
            title_override=custom_title
        )
        
        assert finding.title == custom_title
    
    def test_create_finding_preserves_detection_metadata(self, mock_db, mock_detection):
        """Test that detection metadata is preserved in finding."""
        from app.services.finding_service import FindingService
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        finding = FindingService.create_finding_from_detection(
            db=mock_db,
            detection=mock_detection
        )
        
        assert finding.finding_metadata is not None
        assert finding.finding_metadata["detection_id"] == mock_detection.id
        assert finding.finding_metadata["rule_name"] == "TEST-RULE"
        assert finding.finding_metadata["rule_version"] == "1"


class TestFindingRetrieval:
    """Test finding retrieval operations."""
    
    def test_get_finding_by_id(self, mock_db, mock_finding):
        """Test retrieving a finding by ID."""
        from app.services.finding_service import FindingService
        
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_finding
        mock_db.execute.return_value = mock_result
        
        finding = await FindingService.get_finding_by_id(mock_db, "test-finding-id")
        
        assert finding == mock_finding
        mock_db.execute.assert_called_once()
    
    def test_get_finding_not_found(self, mock_db):
        """Test retrieving a non-existent finding."""
        from app.services.finding_service import FindingService
        
        mock_result = Mock()
        mock_result.scalar_one_ornone.return_value = None
        mock_db.execute.return_value = mock_result
        
        finding = await FindingService.get_finding_by_id(mock_db, "nonexistent-id")
        
        assert finding is None
    
    def test_get_finding_detection(self, mock_db, mock_finding, mock_detection):
        """Test retrieving detection associated with a finding."""
        from app.services.finding_service import FindingService
        
        # Mock finding retrieval
        mock_result_finding = Mock()
        mock_result_finding.scalar_one_or_none.return_value = mock_finding
        mock_db.execute.return_value = mock_result_finding
        
        # Mock detection retrieval
        mock_result_detection = Mock()
        mock_result_detection.scalar_one_or_none.return_value = mock_detection
        mock_db.execute.return_value = mock_result_detection
        
        detection = await FindingService.get_finding_detection(mock_db, "test-finding-id")
        
        assert detection == mock_detection


class TestFindingStatusTransitions:
    """Test finding status transition validation."""
    
    def test_valid_transition_open_to_investigating(self):
        """Test valid transition from OPEN to INVESTIGATING."""
        from app.services.finding_service import FindingService
        
        assert FindingService.is_valid_transition(
            FindingStatus.OPEN,
            FindingStatus.INVESTIGATING
        ) is True
    
    def test_valid_transition_investigating_to_resolved(self):
        """Test valid transition from INVESTIGATING to RESOLVED."""
        from app.services.finding_service import FindingService
        
        assert FindingService.is_valid_transition(
            FindingStatus.INVESTIGATING,
            FindingStatus.RESOLVED
        ) is True
    
    def test_valid_transition_to_false_positive(self):
        """Test valid transition to FALSE_POSITIVE."""
        from app.services.finding_service import FindingService
        
        assert FindingService.is_valid_transition(
            FindingStatus.OPEN,
            FindingStatus.FALSE_POSITIVE
        ) is True
    
    def test_invalid_transition_resolved_to_open(self):
        """Test invalid transition from RESOLVED to OPEN (should be valid)."""
        from app.services.finding_service import FindingService
        
        # RESOLVED can go back to OPEN or INVESTIGATING
        assert FindingService.is_valid_transition(
            FindingStatus.RESOLVED,
            FindingStatus.OPEN
        ) is True
    
    def test_invalid_transition(self):
        """Test invalid status transition."""
        from app.services.finding_service import FindingService
        
        # RESOLVED cannot go directly to FALSE_POSITIVE
        assert FindingService.is_valid_transition(
            FindingStatus.RESOLVED,
            FindingStatus.FALSE_POSITIVE
        ) is False
    
    def test_no_op_transition(self):
        """Test that no-op transitions (same status) are valid."""
        from app.services.finding_service import FindingService
        
        assert FindingService.is_valid_transition(
            FindingStatus.OPEN,
            FindingStatus.OPEN
        ) is True


class TestFindingUpdate:
    """Test finding update operations."""
    
    def test_update_finding_status(self, mock_db, mock_finding):
        """Test updating finding status."""
        from app.services.finding_service import FindingService
        
        # Mock finding retrieval
        mock_result = Mock()
        mock_result.scalar_one_ornone.return_value = mock_finding
        mock_db.execute.return_value = mock_result
        
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        update_data = FindingUpdate(status=FindingStatus.INVESTIGATING)
        updated = await FindingService.update_finding(
            mock_db,
            "test-finding-id",
            update_data
        )
        
        assert updated.status == FindingStatus.INVESTIGATING
    
    def test_update_finding_invalid_status_transition(self, mock_db, mock_finding):
        """Test that invalid status transitions are rejected."""
        from app.services.finding_service import FindingService
        
        mock_result = Mock()
        mock_result.scalar_one_ornone.return_value = mock_finding
        mock_db.execute.return_value = mock_result
        
        # Try invalid transition
        update_data = FindingUpdate(status=FindingStatus.FALSE_POSITIVE)
        mock_finding.status = FindingStatus.RESOLVED  # Can't go directly to FALSE_POSITIVE
        
        with pytest.raises(ValueError) as exc_info:
            await FindingService.update_finding(
                mock_db,
                "test-finding-id",
                update_data
            )
        
        assert "Invalid status transition" in str(exc_info.value)
    
    def test_update_finding_nonexistent(self, mock_db):
        """Test updating a non-existent finding."""
        from app.services.finding_service import FindingService
        
        mock_result = Mock()
        mock_result.scalar_one_ornone.return_value = None
        mock_db.execute.return_value = mock_result
        
        update_data = FindingUpdate(status=FindingStatus.INVESTIGATING)
        updated = await FindingService.update_finding(
            mock_db,
            "nonexistent-id",
            update_data
        )
        
        assert updated is None


class TestFindingFiltering:
    """Test finding filtering and pagination."""
    
    def test_filter_by_severity(self, mock_db):
        """Test filtering findings by severity."""
        from app.services.finding_service import FindingService
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        await FindingService.get_findings(
            mock_db,
            severity="HIGH"
        )
        
        # Verify the query was constructed correctly
        mock_db.execute.assert_called_once()
    
    def test_filter_by_status(self, mock_db):
        """Test filtering findings by status."""
        from app.services.finding_service import FindingService
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        await FindingService.get_findings(
            mock_db,
            status=FindingStatus.OPEN
        )
        
        mock_db.execute.assert_called_once()
    
    def test_pagination(self, mock_db):
        """Test pagination with skip and limit."""
        from app.services.finding_service import FindingService
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        await FindingService.get_findings(
            mock_db,
            skip=10,
            limit=50
        )
        
        mock_db.execute.assert_called_once()


class TestFindingAPI:
    """Test finding API endpoints."""
    
    def test_get_findings_unauthorized(self, client, mock_db):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/v1/findings")
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "unauthorized"
    
    def test_get_findings_authorized(self, client, mock_db):
        """Test that authorized requests succeed."""
        # Mock finding retrieval
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        response = client.get(
            "/api/v1/findings",
            headers={"X-User-ID": "test-user", "X-User-Role": "analyst"}
        )
        
        assert response.status_code == 200
    
    def test_get_finding_by_id_unauthorized(self, client, mock_db):
        """Test that unauthorized individual finding requests are rejected."""
        response = client.get("/api/v1/findings/test-id")
        
        assert response.status_code == 401
    
    def test_update_finding_unauthorized(self, client, mock_db):
        """Test that unauthorized update requests are rejected."""
        response = client.patch(
            "/api/v1/findings/test-id",
            json={"status": "INVESTIGATING"}
        )
        
        assert response.status_code == 401
    
    def test_update_finding_forbidden(self, client, mock_db):
        """Test that forbidden update requests are rejected."""
        # Mock finding exists
        mock_result = Mock()
        mock_result.scalar_one_ornone.return_value = Mock(
            id="test-id",
            status=FindingStatus.OPEN
        )
        mock_db.execute.return_value = mock_result
        
        response = client.patch(
            "/api/v1/findings/test-id",
            json={"status": "INVESTIGATING"},
            headers={"X-User-ID": "test-user", "X-User-Role": "viewer"}
        )
        
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "forbidden"


class TestFindingAudit:
    """Test finding audit logging."""
    
    def test_audit_status_change(self, mock_db):
        """Test that status changes generate audit logs."""
        from app.services.audit_service import AuditService
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        audit_log = AuditService.log_finding_status_change(
            mock_db,
            user_id="test-user",
            finding_id="test-finding",
            old_status="OPEN",
            new_status="INVESTIGATING"
        )
        
        assert audit_log is not None
        mock_db.add.assert_called_once()
    
    def test_audit_resolution(self, mock_db):
        """Test that finding resolutions generate audit logs."""
        from app.services.audit_service import AuditService
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        audit_log = AuditService.log_finding_resolved(
            mock_db,
            user_id="test-user",
            finding_id="test-finding",
            resolution_notes="Investigated and confirmed benign"
        )
        
        assert audit_log is not None
        assert audit_log.action == "finding_resolved"
    
    def test_audit_false_positive(self, mock_db):
        """Test that false positive markings generate audit logs."""
        from app.services.audit_service import AuditService
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        audit_log = AuditService.log_finding_false_positive(
            mock_db,
            user_id="test-user",
            finding_id="test-finding",
            reason="Rule misconfiguration"
        )
        
        assert audit_log is not None
        assert audit_log.action == "finding_marked_false_positive"


class TestFindingRelationships:
    """Test finding relationships with detections and evidence."""
    
    def test_finding_detection_relationship(self, mock_finding, mock_detection):
        """Test that findings maintain detection relationships."""
        assert mock_finding.detection_id == mock_detection.id
    
    def test_finding_metadata_preserves_detection_info(self, mock_finding):
        """Test that finding metadata preserves detection information."""
        assert mock_finding.finding_metadata is not None
        assert "detection_id" in mock_finding.finding_metadata
        assert "rule_name" in mock_finding.finding_metadata
    
    def test_schema_conversion(self, mock_finding):
        """Test conversion between model and schema."""
        from app.services.finding_service import FindingService
        
        schema = FindingService.finding_to_schema(mock_finding)
        
        assert schema.id == mock_finding.id
        assert schema.title == mock_finding.title
        assert schema.status == mock_finding.status
        assert schema.severity == mock_finding.severity