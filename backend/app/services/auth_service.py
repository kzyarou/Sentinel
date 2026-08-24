from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import logging

from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, sanitize_password
from app.core.jwt import create_access_token, verify_token
from app.core.config import settings
from app.core.utils import generate_uuid

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username already exists
        existing_user = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if existing_user.scalar_one_or_none():
            raise ValueError("Username already exists")
        
        # Check if email already exists (if provided)
        if user_data.email:
            existing_email = await db.execute(
                select(User).where(User.email == user_data.email)
            )
            if existing_email.scalar_one_or_none():
                raise ValueError("Email already exists")
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        user = User(
            id=generate_uuid(),
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            role=user_data.role,
            status=user_data.status,
            external_id=user_data.external_id
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Created user: {user.username} (ID: {user.id})")
        
        return user
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        username: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            db: Database session
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Find user by username
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Authentication failed: user not found - {username}")
            return None
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            logger.warning(f"Authentication failed: user not active - {username}")
            return None
        
        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password - {username}")
            return None
        
        logger.info(f"Authentication successful: {username} (ID: {user.id})")
        
        return user
    
    @staticmethod
    async def login_user(
        db: AsyncSession, 
        login_data: UserLogin
    ) -> Dict[str, Any]:
        """
        Login a user and return access token.
        
        Args:
            db: Database session
            login_data: Login credentials
            
        Returns:
            Dictionary with access token and user info
            
        Raises:
            ValueError: If authentication fails
        """
        user = await AuthService.authenticate_user(
            db, 
            login_data.username, 
            login_data.password
        )
        
        if not user:
            raise ValueError("Invalid username or password")
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.id,
                "username": user.username,
                "role": user.role.value
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value
            }
        }
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            db: Database session
            user_id: User ID to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def validate_token_user(db: AsyncSession, token: str) -> Optional[User]:
        """
        Validate a JWT token and return the associated user.
        
        Args:
            db: Database session
            token: JWT token to validate
            
        Returns:
            User object if token valid and user exists, None otherwise
        """
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                return None
            
            user = await AuthService.get_user_by_id(db, user_id)
            
            if not user or user.status != UserStatus.ACTIVE:
                return None
            
            return user
            
        except Exception as e:
            logger.warning(f"Token validation failed: {str(e)}")
            return None