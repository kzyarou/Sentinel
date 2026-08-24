from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from app.models.audit_log import AuditLog
from app.core.utils import generate_uuid

logger = logging.getLogger(__name__)


class AuditService:
    """Service for creating and managing audit logs."""
    
    @staticmethod
    async def create_audit_log(
        db: AsyncSession,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            action: Action performed (e.g., "status_changed", "finding_resolved")
            resource_type: Type of resource (e.g., "finding", "detection")
            resource_id: ID of the resource
            details: Additional details about the action
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        audit_log = AuditLog(
            id=generate_uuid(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        
        logger.info(
            f"Audit log created: user={user_id}, action={action}, "
            f"resource={resource_type}/{resource_id}"
        )
        
        return audit_log
    
    @staticmethod
    async def log_authentication_success(
        db: AsyncSession,
        user_id: str,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a successful authentication event.
        
        Args:
            db: Database session
            user_id: ID of the authenticated user
            username: Username of the authenticated user
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        details = {
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="user_authenticated",
            resource_type="user",
            resource_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_authentication_failure(
        db: AsyncSession,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a failed authentication event.
        
        Args:
            db: Database session
            username: Username that was attempted
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        details = {
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id="unknown",
            action="authentication_failed",
            resource_type="user",
            resource_id="unknown",
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_user_logout(
        db: AsyncSession,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a user logout event.
        
        Args:
            db: Database session
            user_id: ID of the user logging out
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        details = {
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="user_logout",
            resource_type="user",
            resource_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_authorization_failure(
        db: AsyncSession,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        required_permission: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log an authorization failure event.
        
        Args:
            db: Database session
            user_id: ID of the user who was denied access
            action: Action that was attempted
            resource_type: Type of resource accessed
            resource_id: ID of the resource
            required_permission: Permission that was required
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        details = {
            "action": action,
            "required_permission": required_permission,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="authorization_failed",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_finding_status_change(
        db: AsyncSession,
        user_id: str,
        finding_id: str,
        old_status: str,
        new_status: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a finding status change.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            finding_id: ID of the finding
            old_status: Previous status
            new_status: New status
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        details = {
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="finding_status_changed",
            resource_type="finding",
            resource_id=finding_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_finding_resolved(
        db: AsyncSession,
        user_id: str,
        finding_id: str,
        resolution_notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a finding resolution.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            finding_id: ID of the finding
            resolution_notes: Optional notes about the resolution
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        details = {
            "resolution_notes": resolution_notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="finding_resolved",
            resource_type="finding",
            resource_id=finding_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_finding_false_positive(
        db: AsyncSession,
        user_id: str,
        finding_id: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a finding marked as false positive.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            finding_id: ID of the finding
            reason: Optional reason for marking as false positive
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        details = {
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="finding_marked_false_positive",
            resource_type="finding",
            resource_id=finding_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_finding_modified(
        db: AsyncSession,
        user_id: str,
        finding_id: str,
        modified_fields: list,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a finding modification.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            finding_id: ID of the finding
            modified_fields: List of fields that were modified
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        details = {
            "modified_fields": modified_fields,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="finding_modified",
            resource_type="finding",
            resource_id=finding_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )