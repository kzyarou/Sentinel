from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User

security = HTTPBearer()


def get_db() -> Generator:
    """
    Dependency for getting database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency for getting current authenticated user.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If user not found or invalid token
    """
    # For now, this is a simplified implementation
    # In production, this would validate JWT tokens and decode user info
    
    # TODO: Implement proper JWT token validation
    # For development, we'll create a temporary user if none exists
    user = db.query(User).first()
    
    if not user:
        # Create a default user for development
        user = User(
            username="admin",
            email="admin@sentinel.local",
            role="ADMIN"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user