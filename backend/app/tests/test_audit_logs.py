import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime, timedelta
import asyncio

from app.main import app
from app.db.session import get_db, Base
from app.models.audit_log import AuditLog, AuditActionCategory, AuditResult
from app.models.user import User, UserRole, UserStatus
from app.services.audit_service import AuditService
from app.core.security import hash_password
from app.core.utils import generate_uuid


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
async def db_session():
    """Create a test database session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_client(db_session):
    """Create a test client with database dependency override."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestAuditLogModel:
    """Test audit log model structure and constraints."""
    
    @pytest.mark.asyncio
    async def test_audit_log_creation(self, db_session):
        """Test basic audit log creation."""
        audit_log = AuditLog(
            id=generate_uuid(),
            user_id="user123",
            action="test_action",
            action_category=AuditActionCategory.SYSTEM,
            resource_type="test_resource",
            resource_id="resource123",
            result=AuditResult.SUCCESS,
            request_id="req-123",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0",
            audit_metadata={"key": "value"}
        )
        
        db_session.add(audit_log)
        await db_session.commit()
        await db_session.refresh(audit_log)
        
        assert audit_log.id is not None
        assert audit_log.user_id == "user123"
        assert audit_log.action == "test_action"
        assert audit_log.action_category == AuditActionCategory.SYSTEM
        assert audit_log.result == AuditResult.SUCCESS
        assert audit_log.request_id == "req-123"
    
    @pytest.mark.asyncio
    async def test_audit_log_without_user(self, db_session):
        """Test audit log creation without user (system events)."""
        audit_log = AuditLog(
            id=generate_uuid(),
            user_id=None,  # System event
            action="system_event",
            action_category=AuditActionCategory.SYSTEM,
            resource_type="system",
            resource_id=None,
            result=AuditResult.SUCCESS,
            audit_metadata={"event": "system_startup"}
        )
        
        db_session.add(audit_log)
        await db_session.commit()
        await db_session.refresh(audit_log)
        
        assert audit_log.user_id is None
        assert audit_log.action == "system_event"


class TestAuditService:
    """Test audit service functionality."""
    
    @pytest.mark.asyncio
    async def test_create_audit_log(self, db_session):
        """Test basic audit log creation through service."""
        audit_log = await AuditService.create_audit_log(
            db=db_session,
            user_id="user123",
            action="test.action",
            action_category=AuditActionCategory.FINDING,
            resource_type="finding",
            resource_id="finding123",
            result=AuditResult.SUCCESS,
            request_id="req-123",
            metadata={"test": "data"},
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0"
        )
        
        assert audit_log.id is not None
        assert audit_log.action == "test.action"
        assert audit_log.action_category == AuditActionCategory.FINDING
        assert audit_log.result == AuditResult.SUCCESS
    
    @pytest.mark.asyncio
    async def test_metadata_sanitization(self, db_session):
        """Test that sensitive metadata is sanitized."""
        sensitive_metadata = {
            "username": "testuser",
            "password": "secret123",
            "api_key": "key123",
            "normal_field": "normal_value"
        }
        
        audit_log = await AuditService.create_audit_log(
            db=db_session,
            user_id="user123",
            action="test.action",
            action_category=AuditActionCategory.SYSTEM,
            resource_type="test",
            resource_id="test123",
            metadata=sensitive_metadata
        )
        
        # Check that sensitive fields are redacted
        assert audit_log.audit_metadata["username"] == "testuser"
        assert audit_log.audit_metadata["password"] == "[REDACTED]"
        assert audit_log.audit_metadata["api_key"] == "[REDACTED]"
        assert audit_log.audit_metadata["normal_field"] == "normal_value"
    
    @pytest.mark.asyncio
    async def test_log_authentication_success(self, db_session):
        """Test authentication success logging."""
        audit_log = await AuditService.log_authentication_success(
            db=db_session,
            user_id="user123",
            username="testuser",
            request_id="req-123",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0"
        )
        
        assert audit_log.action == "auth.login.success"
        assert audit_log.action_category == AuditActionCategory.AUTHENTICATION
        assert audit_log.result == AuditResult.SUCCESS
        assert audit_log.resource_id == "user123"
    
    @pytest.mark.asyncio
    async def test_log_authentication_failure(self, db_session):
        """Test authentication failure logging."""
        audit_log = await AuditService.log_authentication_failure(
            db=db_session,
            username="testuser",
            request_id="req-123",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0"
        )
        
        assert audit_log.action == "auth.login.failure"
        assert audit_log.action_category == AuditActionCategory.AUTHENTICATION
        assert audit_log.result == AuditResult.FAILURE
        assert audit_log.user_id is None  # No user for failed auth
    
    @pytest.mark.asyncio
    async def test_log_user_logout(self, db_session):
        """Test user logout logging."""
        audit_log = await AuditService.log_user_logout(
            db=db_session,
            user_id="user123",
            request_id="req-123",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0"
        )
        
        assert audit_log.action == "auth.logout"
        assert audit_log.action_category == AuditActionCategory.AUTHENTICATION
        assert audit_log.result == AuditResult.SUCCESS
    
    @pytest.mark.asyncio
    async def test_log_authorization_failure(self, db_session):
        """Test authorization failure logging."""
        audit_log = await AuditService.log_authorization_failure(
            db=db_session,
            user_id="user123",
            attempted_action="delete_finding",
            resource_type="finding",
            resource_id="finding123",
            required_permission="admin",
            request_id="req-123",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0"
        )
        
        assert audit_log.action == "authz.access_denied"
        assert audit_log.action_category == AuditActionCategory.AUTHORIZATION
        assert audit_log.result == AuditResult.FAILURE
    
    @pytest.mark.asyncio
    async def test_log_finding_status_change(self, db_session):
        """Test finding status change logging."""
        audit_log = await AuditService.log_finding_status_change(
            db=db_session,
            user_id="user123",
            finding_id="finding123",
            old_status="OPEN",
            new_status="INVESTIGATING",
            request_id="req-123",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0"
        )
        
        assert audit_log.action == "finding.status_changed"
        assert audit_log.action_category == AuditActionCategory.FINDING
        assert audit_log.result == AuditResult.SUCCESS
        assert audit_log.audit_metadata["old_status"] == "OPEN"
        assert audit_log.audit_metadata["new_status"] == "INVESTIGATING"
    
    @pytest.mark.asyncio
    async def test_log_detection_rule_created(self, db_session):
        """Test detection rule creation logging."""
        audit_log = await AuditService.log_detection_rule_created(
            db=db_session,
            user_id="admin123",
            rule_id="rule123",
            rule_name="Test Rule",
            request_id="req-123",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0"
        )
        
        assert audit_log.action == "detection_rule.created"
        assert audit_log.action_category == AuditActionCategory.DETECTION_RULE
        assert audit_log.result == AuditResult.SUCCESS
    
    @pytest.mark.asyncio
    async def test_log_user_created(self, db_session):
        """Test user creation logging."""
        audit_log = await AuditService.log_user_created(
            db=db_session,
            admin_user_id="admin123",
            created_user_id="user456",
            username="newuser",
            role="ANALYST",
            request_id="req-123",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0"
        )
        
        assert audit_log.action == "user.created"
        assert audit_log.action_category == AuditActionCategory.USER_ADMINISTRATION
        assert audit_log.result == AuditResult.SUCCESS
        assert audit_log.audit_metadata["assigned_role"] == "ANALYST"
    
    @pytest.mark.asyncio
    async def test_critical_audit_logging_failure(self, db_session):
        """Test that critical audit logging raises exception on failure."""
        # Simulate database failure by using invalid session
        from unittest.mock import AsyncMock, patch
        
        with patch.object(db_session, 'add', side_effect=Exception("DB Error")):
            with pytest.raises(Exception) as exc_info:
                await AuditService.create_audit_log_critical(
                    db=db_session,
                    user_id="user123",
                    action="critical_action",
                    action_category=AuditActionCategory.USER_ADMINISTRATION,
                    resource_type="user",
                    resource_id="user123",
                    result=AuditResult.SUCCESS
                )
            
            assert "audit logging failed" in str(exc_info.value)
            assert "Operation prevented" in str(exc_info.value)


class TestAuditLogAPI:
    """Test audit log API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_requires_admin(self, test_client):
        """Test that audit logs endpoint requires admin access."""
        # Create a regular user
        user_data = {
            "username": "analyst",
            "email": "analyst@example.com",
            "password": "TestPassword123!",
            "role": "ANALYST"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        # Login as analyst
        login_response = test_client.post("/api/v1/auth/login", json={
            "username": "analyst",
            "password": "TestPassword123!"
        })
        token = login_response.json()["access_token"]
        
        # Try to access audit logs (should fail)
        response = test_client.get(
            "/api/v1/audit-logs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_with_admin(self, test_client):
        """Test that admin can access audit logs."""
        # Create an admin user
        user_data = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "TestPassword123!",
            "role": "ADMIN"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        # Login as admin
        login_response = test_client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "TestPassword123!"
        })
        token = login_response.json()["access_token"]
        
        # Access audit logs (should succeed)
        response = test_client.get(
            "/api/v1/audit-logs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_audit_log_filtering(self, test_client):
        """Test audit log filtering capabilities."""
        # Create admin user and login
        user_data = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "TestPassword123!",
            "role": "ADMIN"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_response = test_client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "TestPassword123!"
        })
        token = login_response.json()["access_token"]
        
        # Test filtering by action category
        response = test_client.get(
            "/api/v1/audit-logs?action_category=authentication",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Test filtering by result
        response = test_client.get(
            "/api/v1/audit-logs?result=success",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_audit_log_stats(self, test_client):
        """Test audit log statistics endpoint."""
        # Create admin user and login
        user_data = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "TestPassword123!",
            "role": "ADMIN"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_response = test_client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "TestPassword123!"
        })
        token = login_response.json()["access_token"]
        
        # Get audit log statistics
        response = test_client.get(
            "/api/v1/audit-logs/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        stats = response.json()
        assert "total_count" in stats
        assert "category_stats" in stats
        assert "result_stats" in stats
        assert "last_24h_count" in stats


class TestRequestCorrelation:
    """Test request correlation for audit events."""
    
    @pytest.mark.asyncio
    async def test_request_id_in_response_header(self, test_client):
        """Test that request ID is included in response headers."""
        response = test_client.get("/api/v1/health")
        
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0
    
    @pytest.mark.asyncio
    async def test_request_id_persistence(self, test_client):
        """Test that request ID is consistent across request lifecycle."""
        # Get request ID from header
        response = test_client.get("/api/v1/health")
        request_id = response.headers["X-Request-ID"]
        
        # Use same request ID in subsequent request
        response2 = test_client.get(
            "/api/v1/health",
            headers={"X-Request-ID": request_id}
        )
        
        assert response2.headers["X-Request-ID"] == request_id