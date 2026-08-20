from typing import Optional
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)


class AuthorizationError(Exception):
    """Custom exception for authorization failures."""
    pass


class AuthorizationService:
    """Service for handling authorization checks."""
    
    @staticmethod
    def get_current_user(request: Request) -> Optional[dict]:
        """
        Get the current user from the request.
        
        In a production environment, this would extract user information
        from JWT tokens or session cookies. For now, we'll use a simple
        implementation that can be expanded later.
        
        Args:
            request: FastAPI request object
            
        Returns:
            User information dict or None if not authenticated
        """
        # TODO: Implement proper JWT authentication
        # For now, return a mock user or extract from headers
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return {
                "id": user_id,
                "role": request.headers.get("X-User-Role", "analyst")
            }
        return None
    
    @staticmethod
    def require_authentication(request: Request) -> dict:
        """
        Require user to be authenticated.
        
        Args:
            request: FastAPI request object
            
        Returns:
            User information dict
            
        Raises:
            HTTPException: If user is not authenticated
        """
        user = AuthorizationService.get_current_user(request)
        if not user:
            logger.warning("Unauthorized access attempt - no user found")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "unauthorized",
                    "message": "Authentication required"
                }
            )
        return user
    
    @staticmethod
    def require_role(user: dict, required_roles: list) -> None:
        """
        Require user to have specific role(s).
        
        Args:
            user: User information dict
            required_roles: List of required roles
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        user_role = user.get("role", "analyst")
        if user_role not in required_roles:
            logger.warning(
                f"Unauthorized access attempt - user {user.get('id')} "
                f"with role {user_role} attempted to access role-restricted endpoint"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": "Insufficient permissions"
                }
            )
    
    @staticmethod
    def can_modify_finding(user: dict, finding_id: str) -> bool:
        """
        Check if user can modify a specific finding.
        
        In a production environment, this would check ownership or
        team membership. For now, we'll implement a simple role-based check.
        
        Args:
            user: User information dict
            finding_id: Finding ID to check access for
            
        Returns:
            True if user can modify, False otherwise
        """
        user_role = user.get("role", "analyst")
        
        # Admins and security analysts can modify findings
        if user_role in ["admin", "security_analyst"]:
            return True
        
        # Regular analysts can only modify findings they created
        # TODO: Implement ownership checking
        if user_role == "analyst":
            logger.debug(f"Analyst {user.get('id')} requesting access to finding {finding_id}")
            return True  # Allow for now, implement ownership later
        
        return False
    
    @staticmethod
    def can_view_finding(user: dict, finding_id: str) -> bool:
        """
        Check if user can view a specific finding.
        
        Args:
            user: User information dict
            finding_id: Finding ID to check access for
            
        Returns:
            True if user can view, False otherwise
        """
        user_role = user.get("role", "analyst")
        
        # All authenticated users can view findings
        if user_role in ["admin", "security_analyst", "analyst", "viewer"]:
            return True
        
        return False
    
    @staticmethod
    def require_finding_modify_permission(user: dict, finding_id: str) -> None:
        """
        Require user to have permission to modify a finding.
        
        Args:
            user: User information dict
            finding_id: Finding ID to check access for
            
        Raises:
            HTTPException: If user doesn't have modify permission
        """
        if not AuthorizationService.can_modify_finding(user, finding_id):
            logger.warning(
                f"Unauthorized modification attempt - user {user.get('id')} "
                f"attempted to modify finding {finding_id}"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": "Insufficient permissions to modify this finding"
                }
            )
    
    @staticmethod
    def require_finding_view_permission(user: dict, finding_id: str) -> None:
        """
        Require user to have permission to view a finding.
        
        Args:
            user: User information dict
            finding_id: Finding ID to check access for
            
        Raises:
            HTTPException: If user doesn't have view permission
        """
        if not AuthorizationService.can_view_finding(user, finding_id):
            logger.warning(
                f"Unauthorized view attempt - user {user.get('id')} "
                f"attempted to view finding {finding_id}"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": "Insufficient permissions to view this finding"
                }
            )