import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import asyncio

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, verify_token
from app.core.config import settings


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


class TestPasswordSecurity:
    """Test password security functions."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20  # Bcrypt hashes are typically 60 chars
        assert password not in hashed
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_hash_uniqueness(self):
        """Test that the same password generates different hashes."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Due to salt


class TestJWTTokens:
    """Test JWT token generation and validation."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "user123", "role": "ANALYST"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
    
    def test_verify_valid_token(self):
        """Test verification of valid token."""
        data = {"sub": "user123", "role": "ANALYST"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload["sub"] == "user123"
        assert payload["role"] == "ANALYST"
        assert "exp" in payload
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):  # HTTPException in production
            verify_token(invalid_token)
    
    def test_token_expiration(self):
        """Test token expiration."""
        # Create token with very short expiration
        data = {"sub": "user123", "role": "ANALYST"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(Exception):  # Should raise due to expiration
            verify_token(token)


class TestAuthentication:
    """Test authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user(self, test_client, db_session):
        """Test user registration."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "ANALYST"
        }
        
        response = test_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "ANALYST"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, test_client, db_session):
        """Test registration with duplicate username."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "ANALYST"
        }
        
        # First registration
        test_client.post("/api/v1/auth/register", json=user_data)
        
        # Second registration with same username
        response = test_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "validation_error" in response.json()["error"]
    
    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, test_client, db_session):
        """Test login with valid credentials."""
        # First register a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "ANALYST"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        # Now login
        login_data = {
            "username": "testuser",
            "password": "TestPassword123!"
        }
        response = test_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, test_client, db_session):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = test_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "authentication_failed" in response.json()["error"]
    
    @pytest.mark.asyncio
    async def test_login_with_token(self, test_client, db_session):
        """Test using token to access protected endpoint."""
        # Register and login
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "ANALYST"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "testuser",
            "password": "TestPassword123!"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Access protected endpoint with token
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/api/v1/findings", headers=headers)
        
        assert response.status_code == 200


class TestAuthorization:
    """Test authorization and role-based access control."""
    
    @pytest.mark.asyncio
    async def test_analyst_can_view_findings(self, test_client, db_session):
        """Test that analysts can view findings."""
        # Register and login as analyst
        user_data = {
            "username": "analyst",
            "email": "analyst@example.com",
            "password": "TestPassword123!",
            "role": "ANALYST"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "analyst",
            "password": "TestPassword123!"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Try to access findings
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/api/v1/findings", headers=headers)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_viewer_cannot_modify_findings(self, test_client, db_session):
        """Test that viewers cannot modify findings."""
        # Register and login as viewer
        user_data = {
            "username": "viewer",
            "email": "viewer@example.com",
            "password": "TestPassword123!",
            "role": "VIEWER"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "viewer",
            "password": "TestPassword123!"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Try to modify a finding (should fail)
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {"status": "RESOLVED"}
        response = test_client.patch(
            "/api/v1/findings/test-finding-id",
            json=update_data,
            headers=headers
        )
        
        # Should fail with 403 or 404 (depending on finding existence)
        assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_admin_can_manage_detection_rules(self, test_client, db_session):
        """Test that admins can manage detection rules."""
        # Register and login as admin
        user_data = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "TestPassword123!",
            "role": "ADMIN"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "admin",
            "password": "TestPassword123!"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Try to seed detection rules
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.post("/api/v1/detections/seed-rules", headers=headers)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_analyst_cannot_manage_detection_rules(self, test_client, db_session):
        """Test that analysts cannot manage detection rules."""
        # Register and login as analyst
        user_data = {
            "username": "analyst",
            "email": "analyst@example.com",
            "password": "TestPassword123!",
            "role": "ANALYST"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "analyst",
            "password": "TestPassword123!"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Try to seed detection rules (should fail)
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.post("/api/v1/detections/seed-rules", headers=headers)
        
        assert response.status_code == 403


class TestSecurity:
    """Test security aspects of authentication."""
    
    @pytest.mark.asyncio
    async def test_unauthenticated_access_denied(self, test_client, db_session):
        """Test that unauthenticated requests are denied."""
        response = test_client.get("/api/v1/findings")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_token_denied(self, test_client, db_session):
        """Test that invalid tokens are denied."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/api/v1/findings", headers=headers)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_expired_token_denied(self, test_client, db_session):
        """Test that expired tokens are denied."""
        # Create an expired token
        data = {"sub": "user123", "role": "ANALYST"}
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = test_client.get("/api/v1/findings", headers=headers)
        
        assert response.status_code == 401