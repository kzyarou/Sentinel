from typing import Optional, List
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
import logging

logger = logging.getLogger(__name__)


class AuthorizationError(Exception):
    """Custom exception for authorization failures."""
    pass


class AuthorizationService:
    """Service for handling authorization checks."""
    
    @staticmethod
    def require_role(user: User, required_roles: List[UserRole], db: AsyncSession = None, request = None) -> None:
        """
        Require user to have specific role(s).
        
        Args:
            user: User object
            required_roles: List of required roles
            db: Optional database session for audit logging
            request: Optional request object for audit logging
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        if user.role not in required_roles:
            logger.warning(
                f"Unauthorized access attempt - user {user.id} "
                f"with role {user.role.value} attempted to access role-restricted endpoint"
            )
            
            # Log authorization failure if db and request are provided
            if db and request:
                from app.services.audit_service import AuditService
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
                
                import asyncio
                asyncio.create_task(AuditService.log_authorization_failure(
                    db=db,
                    user_id=user.id,
                    action="role_based_access_denied",
                    resource_type="endpoint",
                    resource_id="unknown",
                    required_permission=f"role: {required_roles}",
                    ip_address=ip_address,
                    user_agent=user_agent
                ))
            
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": "Insufficient permissions"
                }
            )
    
    @staticmethod
    def can_modify_finding(user: User, finding_id: str) -> bool:
        """
        Check if user can modify a specific finding.
        
        Args:
            user: User object
            finding_id: Finding ID to check access for
            
        Returns:
            True if user can modify, False otherwise
        """
        # Admins can modify any finding
        if user.role == UserRole.ADMIN:
            return True
        
        # Analysts can modify findings
        if user.role == UserRole.ANALYST:
            logger.debug(f"Analyst {user.id} requesting access to finding {finding_id}")
            return True  # Allow for now, implement ownership later
        
        # Viewers cannot modify findings
        return False
    
    @staticmethod
    def can_view_finding(user: User, finding_id: str) -> bool:
        """
        Check if user can view a specific finding.
        
        Args:
            user: User object
            finding_id: Finding ID to check access for
            
        Returns:
            True if user can view, False otherwise
        """
        # All authenticated users can view findings
        return True
    
    @staticmethod
    def can_request_ai_analysis(user: User) -> bool:
        """
        Check if user can request AI analysis.
        
        Args:
            user: User object
            
        Returns:
            True if user can request AI analysis, False otherwise
        """
        # Admins and Analysts can request AI analysis
        return user.role in [UserRole.ADMIN, UserRole.ANALYST]
    
    @staticmethod
    def can_manage_detection_rules(user: User) -> bool:
        """
        Check if user can manage detection rules.
        
        Args:
            user: User object
            
        Returns:
            True if user can manage detection rules, False otherwise
        """
        # Only Admins can manage detection rules
        return user.role == UserRole.ADMIN
    
    @staticmethod
    def can_manage_users(user: User) -> bool:
        """
        Check if user can manage users.
        
        Args:
            user: User object
            
        Returns:
            True if user can manage users, False otherwise
        """
        # Only Admins can manage users
        return user.role == UserRole.ADMIN
    
    @staticmethod
    def can_view_audit_logs(user: User) -> bool:
        """
        Check if user can view audit logs.
        
        Args:
            user: User object
            
        Returns:
            True if user can view audit logs, False otherwise
        """
        # Only Admins can view audit logs
        return user.role == UserRole.ADMIN
    
    @staticmethod
    def require_finding_modify_permission(user: User, finding_id: str) -> None:
        """
        Require user to have permission to modify a finding.
        
        Args:
            user: User object
            finding_id: Finding ID to check access for
            
        Raises:
            HTTPException: If user doesn't have modify permission
        """
        if not AuthorizationService.can_modify_finding(user, finding_id):
            logger.warning(
                f"Unauthorized modification attempt - user {user.id} "
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
    def require_finding_view_permission(user: User, finding_id: str) -> None:
        """
        Require user to have permission to view a finding.
        
        Args:
            user: User object
            finding_id: Finding ID to check access for
            
        Raises:
            HTTPException: If user doesn't have view permission
        """
        if not AuthorizationService.can_view_finding(user, finding_id):
            logger.warning(
                f"Unauthorized view attempt - user {user.id} "
                f"attempted to view finding {finding_id}"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": "Insufficient permissions to view this finding"
                }
            )
    
    @staticmethod
    def require_ai_analysis_permission(user: User) -> None:
        """
        Require user to have permission to request AI analysis.
        
        Args:
            user: User object
            
        Raises:
            HTTPException: If user doesn't have AI analysis permission
        """
        if not AuthorizationService.can_request_ai_analysis(user):
            logger.warning(
                f"Unauthorized AI analysis attempt - user {user.id} "
                f"with role {user.role.value}"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": "Insufficient permissions to request AI analysis"
                }
            )
    
    @staticmethod
    def require_detection_rule_management_permission(user: User) -> None:
        """
        Require user to have permission to manage detection rules.
        
        Args:
            user: User object
            
        Raises:
            HTTPException: If user doesn't have detection rule management permission
        """
        if not AuthorizationService.can_manage_detection_rules(user):
            logger.warning(
                f"Unauthorized detection rule management attempt - user {user.id} "
                f"with role {user.role.value}"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": "Insufficient permissions to manage detection rules"
                }
            )
    
    @staticmethod
    def require_user_management_permission(user: User) -> None:
        """
        Require user to have permission to manage users.
        
        Args:
            user: User object
            
        Raises:
            HTTPException: If user doesn't have user management permission
        """
        if not AuthorizationService.can_manage_users(user):
            logger.warning(
                f"Unauthorized user management attempt - user {user.id} "
                f"with role {user.role.value}"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": "Insufficient permissions to manage users"
                }
            )
    
    @staticmethod
    def require_audit_log_permission(user: User) -> None:
        """
        Require user to have permission to view audit logs.
        
        Args:
            user: User object
            
        Raises:
            HTTPException: If user doesn't have audit log permission
        """
        if not AuthorizationService.can_view_audit_logs(user):
            logger.warning(
                f"Unauthorized audit log access attempt - user {user.id} "
                f"with role {user.role.value}"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": "Insufficient permissions to view audit logs"
                }
            )