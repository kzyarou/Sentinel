from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.detection_rule import (
    DetectionRule as DetectionRuleSchema,
    DetectionRuleCreate,
    DetectionRuleUpdate
)
from app.services.detection_rule_service import DetectionRuleService
from app.services.audit_service import AuditService
from app.api.v1.endpoints.dependencies import get_current_user, get_request_id
from app.models.user import User
from app.core.authorization import AuthorizationService
from app.services.rule_validation import RuleValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/detection-rules", response_model=DetectionRuleSchema)
async def create_detection_rule(
    rule_data: DetectionRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Depends(get_request_id)
):
    """
    Create a new detection rule.
    
    Requires administrator privileges.
    
    Args:
        rule_data: Rule creation data
        current_user: Current authenticated user
        db: Database session
        request_id: Request ID for correlation
        
    Returns:
        Created detection rule
    """
    try:
        # Check if user has permission to manage detection rules
        AuthorizationService.require_detection_rule_management_permission(current_user)
        
        # Create services
        audit_service = AuditService(db)
        rule_service = DetectionRuleService(db, audit_service)
        
        # Create the rule
        rule = await rule_service.create_rule(
            rule_data=rule_data,
            user_id=current_user.id
        )
        
        return rule
        
    except RuleValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error creating detection rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to create detection rule")


@router.get("/detection-rules/{rule_id}", response_model=DetectionRuleSchema)
async def get_detection_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a detection rule by ID.
    
    Both analysts and administrators can view rules.
    
    Args:
        rule_id: Rule ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Detection rule
    """
    try:
        # Create services
        audit_service = AuditService(db)
        rule_service = DetectionRuleService(db, audit_service)
        
        # Get the rule
        rule = await rule_service.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Detection rule not found")
        
        return rule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting detection rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to get detection rule")


@router.get("/detection-rules", response_model=dict)
async def get_detection_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detection rules with filtering and pagination.
    
    Both analysts and administrators can view rules.
    
    Args:
        skip: Number of rules to skip
        limit: Maximum number of rules to return
        category: Filter by category
        severity: Filter by severity
        enabled: Filter by enabled state
        search: Search in name and description
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dictionary with rules list and total count
    """
    try:
        # Create services
        audit_service = AuditService(db)
        rule_service = DetectionRuleService(db, audit_service)
        
        # Get rules
        rules, total = await rule_service.get_rules(
            skip=skip,
            limit=limit,
            category=category,
            severity=severity,
            enabled=enabled,
            search=search
        )
        
        return {
            "items": rules,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting detection rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to get detection rules")


@router.patch("/detection-rules/{rule_id}", response_model=DetectionRuleSchema)
async def update_detection_rule(
    rule_id: str,
    rule_data: DetectionRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Depends(get_request_id)
):
    """
    Update a detection rule.
    
    Requires administrator privileges.
    Name and version cannot be changed - create a new version instead.
    
    Args:
        rule_id: Rule ID
        rule_data: Rule update data
        current_user: Current authenticated user
        db: Database session
        request_id: Request ID for correlation
        
    Returns:
        Updated detection rule
    """
    try:
        # Check if user has permission to manage detection rules
        AuthorizationService.require_detection_rule_management_permission(current_user)
        
        # Create services
        audit_service = AuditService(db)
        rule_service = DetectionRuleService(db, audit_service)
        
        # Update the rule
        rule = await rule_service.update_rule(
            rule_id=rule_id,
            rule_data=rule_data,
            user_id=current_user.id
        )
        
        if not rule:
            raise HTTPException(status_code=404, detail="Detection rule not found")
        
        return rule
        
    except RuleValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating detection rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to update detection rule")


@router.post("/detection-rules/{rule_id}/enable", response_model=DetectionRuleSchema)
async def enable_detection_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Depends(get_request_id)
):
    """
    Enable a detection rule.
    
    Requires administrator privileges.
    
    Args:
        rule_id: Rule ID
        current_user: Current authenticated user
        db: Database session
        request_id: Request ID for correlation
        
    Returns:
        Enabled detection rule
    """
    try:
        # Check if user has permission to manage detection rules
        AuthorizationService.require_detection_rule_management_permission(current_user)
        
        # Create services
        audit_service = AuditService(db)
        rule_service = DetectionRuleService(db, audit_service)
        
        # Enable the rule
        rule = await rule_service.enable_rule(
            rule_id=rule_id,
            user_id=current_user.id
        )
        
        if not rule:
            raise HTTPException(status_code=404, detail="Detection rule not found")
        
        return rule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling detection rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable detection rule")


@router.post("/detection-rules/{rule_id}/disable", response_model=DetectionRuleSchema)
async def disable_detection_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Depends(get_request_id)
):
    """
    Disable a detection rule.
    
    Requires administrator privileges.
    
    Args:
        rule_id: Rule ID
        current_user: Current authenticated user
        db: Database session
        request_id: Request ID for correlation
        
    Returns:
        Disabled detection rule
    """
    try:
        # Check if user has permission to manage detection rules
        AuthorizationService.require_detection_rule_management_permission(current_user)
        
        # Create services
        audit_service = AuditService(db)
        rule_service = DetectionRuleService(db, audit_service)
        
        # Disable the rule
        rule = await rule_service.disable_rule(
            rule_id=rule_id,
            user_id=current_user.id
        )
        
        if not rule:
            raise HTTPException(status_code=404, detail="Detection rule not found")
        
        return rule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling detection rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable detection rule")


@router.get("/detection-rules/by-name/{rule_name}", response_model=List[DetectionRuleSchema])
async def get_detection_rule_versions(
    rule_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all versions of a detection rule by name.
    
    Both analysts and administrators can view rule versions.
    
    Args:
        rule_name: Rule name
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of detection rule versions
    """
    try:
        # Create services
        audit_service = AuditService(db)
        rule_service = DetectionRuleService(db, audit_service)
        
        # Get rule versions
        rules = await rule_service.get_rule_versions(rule_name)
        
        return rules
        
    except Exception as e:
        logger.error(f"Error getting detection rule versions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get detection rule versions")


@router.delete("/detection-rules/{rule_id}", response_model=dict)
async def delete_detection_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Depends(get_request_id)
):
    """
    Delete a detection rule.
    
    Requires administrator privileges.
    Rules with associated detections are disabled instead of deleted.
    
    Args:
        rule_id: Rule ID
        current_user: Current authenticated user
        db: Database session
        request_id: Request ID for correlation
        
    Returns:
        Dictionary with deletion status
    """
    try:
        # Check if user has permission to manage detection rules
        AuthorizationService.require_detection_rule_management_permission(current_user)
        
        # Create services
        audit_service = AuditService(db)
        rule_service = DetectionRuleService(db, audit_service)
        
        # Delete the rule
        deleted = await rule_service.delete_rule(
            rule_id=rule_id,
            user_id=current_user.id
        )
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Detection rule not found")
        
        return {
            "status": "success",
            "message": "Detection rule deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting detection rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete detection rule")