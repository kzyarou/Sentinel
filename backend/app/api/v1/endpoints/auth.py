from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.api.v1.endpoints.dependencies import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/auth/login", response_model=Dict[str, Any])
async def login(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate a user and return an access token.
    
    Args:
        login_data: Login credentials (username, password)
        request: FastAPI request object
        db: Database session
        
    Returns:
        Dictionary with access token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Extract client information for audit logging
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Attempt authentication
        result = await AuthService.login_user(db, login_data)
        
        # Log successful authentication
        user_id = result["user"]["id"]
        await AuditService.log_authentication_success(
            db=db,
            user_id=user_id,
            username=login_data.username,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"User logged in: {login_data.username}")
        
        return result
        
    except ValueError as e:
        # Log failed authentication attempt
        logger.warning(f"Failed login attempt for username: {login_data.username}")
        
        # Create audit log for failed authentication (without revealing if user exists)
        await AuditService.log_authentication_failure(
            db=db,
            username=login_data.username,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        raise HTTPException(
            status_code=401,
            detail={
                "error": "authentication_failed",
                "message": "Invalid username or password"
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred during login"
            }
        )


@router.post("/auth/register", response_model=Dict[str, Any])
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    This endpoint creates a new user account. In production, this would typically
    be restricted to administrators or require additional verification.
    
    Args:
        user_data: User creation data
        request: FastAPI request object
        db: Database session
        
    Returns:
        Dictionary with created user information
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        # Extract client information for audit logging
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Create user
        user = await AuthService.create_user(db, user_data)
        
        # Log user creation
        await AuditService.create_audit_log(
            db=db,
            user_id=user.id,
            action="user_created",
            resource_type="user",
            resource_id=user.id,
            details={
                "username": user.username,
                "email": user.email,
                "role": user.role.value
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"User registered: {user.username}")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "status": user.status.value,
            "created_timestamp": user.created_timestamp.isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred during registration"
            }
        )


@router.post("/auth/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout a user.
    
    Since we're using stateless JWT tokens, logout is primarily for audit logging.
    Client-side token management is the responsibility of the client application.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        # Extract client information for audit logging
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Log user logout
        await AuditService.log_user_logout(
            db=db,
            user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"User logged out: {current_user.username}")
        
        return {
            "message": "Successfully logged out"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error during logout: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred during logout"
            }
        )