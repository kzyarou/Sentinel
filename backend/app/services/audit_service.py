from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from app.models.audit_log import AuditLog, AuditActionCategory, AuditResult
from app.core.utils import generate_uuid

logger = logging.getLogger(__name__)


class AuditService:
    """Service for creating and managing audit logs."""
    
    @staticmethod
    async def create_audit_log(
        db: AsyncSession,
        user_id: Optional[str],
        action: str,
        action_category: AuditActionCategory,
        resource_type: str,
        resource_id: Optional[str],
        result: AuditResult = AuditResult.SUCCESS,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action (None for system events)
            action: Action performed (e.g., "status_changed", "finding_resolved")
            action_category: Category of the action (authentication, authorization, etc.)
            resource_type: Type of resource (e.g., "finding", "detection")
            resource_id: ID of the resource
            result: Result of the action (success, failure, error)
            request_id: Request ID for correlation
            metadata: Additional metadata about the action (sanitized)
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        # Sanitize metadata to remove sensitive information
        sanitized_metadata = AuditService._sanitize_metadata(metadata or {})
        
        audit_log = AuditLog(
            id=generate_uuid(),
            user_id=user_id,
            action=action,
            action_category=action_category,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
            audit_metadata=sanitized_metadata
        )
        
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        
        logger.info(
            f"Audit log created: user={user_id}, action={action}, "
            f"category={action_category.value}, resource={resource_type}/{resource_id}, "
            f"result={result.value}"
        )
        
        return audit_log
    
    @staticmethod
    def _sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata to remove sensitive information.
        
        Args:
            metadata: Original metadata dictionary
            
        Returns:
            Sanitized metadata dictionary
        """
        sensitive_keys = [
            'password', 'token', 'secret', 'key', 'credential', 'auth',
            'authorization', 'bearer', 'jwt', 'api_key', 'access_token'
        ]
        
        sanitized = {}
        for key, value in metadata.items():
            # Check if key contains sensitive terms
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 1000:
                # Truncate very long strings
                sanitized[key] = value[:1000] + "... (truncated)"
        else:
            sanitized[key] = value
        
        return sanitized
    
    async def log_detection_rule_created(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule creation."""
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.created",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata={
                "rule_name": rule_name,
                "rule_version": rule_version
            }
        )
    
    async def log_detection_rule_updated(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        changes: List[str],
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule update."""
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.updated",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata={
                "rule_name": rule_name,
                "rule_version": rule_version,
                "changes": changes
            }
        )
    
    async def log_detection_rule_enabled(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule enable."""
        metadata = {
            "rule_name": rule_name,
            "rule_version": rule_version
        }
        if reason:
            metadata["reason"] = reason
        
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.enabled",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata=metadata
        )
    
    async def log_detection_rule_disabled(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule disable."""
        metadata = {
            "rule_name": rule_name,
            "rule_version": rule_version
        }
        if reason:
            metadata["reason"] = reason
        
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.disabled",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata=metadata
        )
    
    async def log_detection_rule_deleted(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule deletion."""
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.deleted",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata={
                "rule_name": rule_name,
                "rule_version": rule_version
            }
        )
                sanitized[key] = value[:1000] + "... [TRUNCATED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def log_detection_rule_created(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule creation."""
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.created",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata={
                "rule_name": rule_name,
                "rule_version": rule_version
            }
        )
    
    async def log_detection_rule_updated(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        changes: List[str],
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule update."""
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.updated",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata={
                "rule_name": rule_name,
                "rule_version": rule_version,
                "changes": changes
            }
        )
    
    async def log_detection_rule_enabled(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule enable."""
        metadata = {
            "rule_name": rule_name,
            "rule_version": rule_version
        }
        if reason:
            metadata["reason"] = reason
        
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.enabled",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata=metadata
        )
    
    async def log_detection_rule_disabled(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule disable."""
        metadata = {
            "rule_name": rule_name,
            "rule_version": rule_version
        }
        if reason:
            metadata["reason"] = reason
        
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.disabled",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata=metadata
        )
    
    async def log_detection_rule_deleted(
        self,
        rule_id: str,
        rule_name: str,
        rule_version: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """Log detection rule deletion."""
        return await self.create_audit_log(
            db=self.db,
            user_id=user_id,
            action="detection_rule.deleted",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            request_id=request_id,
            metadata={
                "rule_name": rule_name,
                "rule_version": rule_version
            }
        )
    
    @staticmethod
    async def create_audit_log_critical(
        db: AsyncSession,
        user_id: Optional[str],
        action: str,
        action_category: AuditActionCategory,
        resource_type: str,
        resource_id: Optional[str],
        result: AuditResult = AuditResult.SUCCESS,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Create a critical audit log entry. Critical operations are prevented if audit logging fails.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action (None for system events)
            action: Action performed
            action_category: Category of the action
            resource_type: Type of resource
            resource_id: ID of the resource
            result: Result of the action
            request_id: Request ID for correlation
            metadata: Additional metadata about the action (sanitized)
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
            
        Raises:
            Exception: If audit logging fails, with message indicating operation was prevented
        """
        try:
            return await AuditService.create_audit_log(
                db=db,
                user_id=user_id,
                action=action,
                action_category=action_category,
                resource_type=resource_type,
                resource_id=resource_id,
                result=result,
                request_id=request_id,
                metadata=metadata,
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            logger.error(f"Critical audit logging failed: {e}")
            raise Exception(f"audit logging failed: {e}. Operation prevented for security reasons.") from e
    
    @staticmethod
    async def log_authentication_success(
        db: AsyncSession,
        user_id: str,
        username: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a successful authentication event.
        
        Args:
            db: Database session
            user_id: ID of the authenticated user
            username: Username of the authenticated user
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="auth.login.success",
            action_category=AuditActionCategory.AUTHENTICATION,
            resource_type="user",
            resource_id=user_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_authentication_failure(
        db: AsyncSession,
        username: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a failed authentication event.
        
        Args:
            db: Database session
            username: Username that was attempted
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=None,  # No user ID for failed auth
            action="auth.login.failure",
            action_category=AuditActionCategory.AUTHENTICATION,
            resource_type="user",
            resource_id="unknown",
            result=AuditResult.FAILURE,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_user_logout(
        db: AsyncSession,
        user_id: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a user logout event.
        
        Args:
            db: Database session
            user_id: ID of the user logging out
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="auth.logout",
            action_category=AuditActionCategory.AUTHENTICATION,
            resource_type="user",
            resource_id=user_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_authorization_failure(
        db: AsyncSession,
        user_id: str,
        attempted_action: str,
        resource_type: str,
        resource_id: str,
        required_permission: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log an authorization failure event.
        
        Args:
            db: Database session
            user_id: ID of the user who was denied access
            attempted_action: Action that was attempted
            resource_type: Type of resource accessed
            resource_id: ID of the resource
            required_permission: Permission that was required
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "attempted_action": attempted_action,
            "required_permission": required_permission,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="authz.access_denied",
            action_category=AuditActionCategory.AUTHORIZATION,
            resource_type=resource_type,
            resource_id=resource_id,
            result=AuditResult.FAILURE,
            request_id=request_id,
            metadata=metadata,
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
        request_id: Optional[str] = None,
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
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="finding.status_changed",
            action_category=AuditActionCategory.FINDING,
            resource_type="finding",
            resource_id=finding_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_finding_resolved(
        db: AsyncSession,
        user_id: str,
        finding_id: str,
        resolution_notes: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a finding resolution.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            finding_id: ID of the finding
            resolution_notes: Optional resolution notes
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "resolution_notes": resolution_notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="finding.resolved",
            action_category=AuditActionCategory.FINDING,
            resource_type="finding",
            resource_id=finding_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_finding_false_positive(
        db: AsyncSession,
        user_id: str,
        finding_id: str,
        reason: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a finding marked as false positive.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            finding_id: ID of the finding
            reason: Optional reason for false positive marking
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="finding.false_positive",
            action_category=AuditActionCategory.FINDING,
            resource_type="finding",
            resource_id=finding_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_finding_modified(
        db: AsyncSession,
        user_id: str,
        finding_id: str,
        modified_fields: Dict[str, Any],
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a finding modification.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            finding_id: ID of the finding
            modified_fields: Dictionary of modified fields
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "modified_fields": modified_fields,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="finding.modified",
            action_category=AuditActionCategory.FINDING,
            resource_type="finding",
            resource_id=finding_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_detection_rule_created(
        db: AsyncSession,
        user_id: str,
        rule_id: str,
        rule_name: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a detection rule creation.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            rule_id: ID of the detection rule
            rule_name: Name of the detection rule
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "rule_name": rule_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="detection_rule.created",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_detection_rule_updated(
        db: AsyncSession,
        user_id: str,
        rule_id: str,
        rule_name: str,
        updated_fields: Dict[str, Any],
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a detection rule update.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            rule_id: ID of the detection rule
            rule_name: Name of the detection rule
            updated_fields: Dictionary of updated fields
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "rule_name": rule_name,
            "updated_fields": updated_fields,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="detection_rule.updated",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_detection_rule_enabled(
        db: AsyncSession,
        user_id: str,
        rule_id: str,
        rule_name: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a detection rule being enabled.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            rule_id: ID of the detection rule
            rule_name: Name of the detection rule
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "rule_name": rule_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="detection_rule.enabled",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_detection_rule_disabled(
        db: AsyncSession,
        user_id: str,
        rule_id: str,
        rule_name: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a detection rule being disabled.
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            rule_id: ID of the detection rule
            rule_name: Name of the detection rule
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "rule_name": rule_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=user_id,
            action="detection_rule.disabled",
            action_category=AuditActionCategory.DETECTION_RULE,
            resource_type="detection_rule",
            resource_id=rule_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_user_created(
        db: AsyncSession,
        admin_user_id: str,
        created_user_id: str,
        username: str,
        role: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a user creation (critical operation).
        
        Args:
            db: Database session
            admin_user_id: ID of the admin performing the action
            created_user_id: ID of the created user
            username: Username of the created user
            role: Role assigned to the user
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "username": username,
            "assigned_role": role,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log_critical(
            db=db,
            user_id=admin_user_id,
            action="user.created",
            action_category=AuditActionCategory.USER_ADMINISTRATION,
            resource_type="user",
            resource_id=created_user_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_user_updated(
        db: AsyncSession,
        admin_user_id: str,
        target_user_id: str,
        updated_fields: Dict[str, Any],
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a user update.
        
        Args:
            db: Database session
            admin_user_id: ID of the admin performing the action
            target_user_id: ID of the user being updated
            updated_fields: Dictionary of updated fields
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "updated_fields": updated_fields,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log(
            db=db,
            user_id=admin_user_id,
            action="user.updated",
            action_category=AuditActionCategory.USER_ADMINISTRATION,
            resource_type="user",
            resource_id=target_user_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_user_role_changed(
        db: AsyncSession,
        admin_user_id: str,
        target_user_id: str,
        old_role: str,
        new_role: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a user role change (critical operation).
        
        Args:
            db: Database session
            admin_user_id: ID of the admin performing the action
            target_user_id: ID of the user whose role was changed
            old_role: Previous role
            new_role: New role
            request_id: Request ID for correlation
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Created AuditLog object
        """
        metadata = {
            "old_role": old_role,
            "new_role": new_role,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await AuditService.create_audit_log_critical(
            db=db,
            user_id=admin_user_id,
            action="user.role_changed",
            action_category=AuditActionCategory.USER_ADMINISTRATION,
            resource_type="user",
            resource_id=target_user_id,
            result=AuditResult.SUCCESS,
            request_id=request_id,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )