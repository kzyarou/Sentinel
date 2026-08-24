from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.session import get_db
from app.schemas.finding import Finding as FindingSchema, FindingUpdate, FindingStatus
from app.services.finding_service import FindingService
from app.models.finding import FindingStatus as FindingStatusEnum
from app.core.authorization import AuthorizationService
from app.api.v1.endpoints.dependencies import get_current_user
from app.models.user import User
from app.core.request_id import get_request_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/findings", response_model=List[FindingSchema])
async def get_findings(
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    severity: Optional[str] = Query(None, description="Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)"),
    status: Optional[FindingStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve findings with optional filtering and pagination.
    
    Args:
        skip: Number of results to skip (pagination)
        limit: Maximum number of results to return
        severity: Optional severity filter
        status: Optional status filter
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of findings matching the criteria
    """
    try:
        # Convert status string to enum if provided
        status_enum = None
        if status:
            status_enum = FindingStatusEnum(status.value)
        
        findings = await FindingService.get_findings(
            db=db,
            skip=skip,
            limit=limit,
            severity=severity,
            status=status_enum
        )
        
        # Filter findings based on user permissions
        accessible_findings = []
        for finding in findings:
            if AuthorizationService.can_view_finding(current_user, finding.id):
                accessible_findings.append(finding)
        
        return [FindingService.finding_to_schema(finding) for finding in accessible_findings]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving findings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to retrieve findings"
            }
        )


@router.get("/findings/{finding_id}", response_model=FindingSchema)
async def get_finding(
    finding_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific finding by ID.
    
    Args:
        finding_id: Finding ID to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Finding object if found
        
    Raises:
        HTTPException: If finding not found or access denied
    """
    try:
        finding = await FindingService.get_finding_by_id(db, finding_id)
        
        if not finding:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"Finding with ID {finding_id} not found"
                }
            )
        
        # Check view permission
        AuthorizationService.require_finding_view_permission(current_user, finding_id)
        
        return FindingService.finding_to_schema(finding)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving finding {finding_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to retrieve finding"
            }
        )


@router.patch("/findings/{finding_id}", response_model=FindingSchema)
async def update_finding(
    finding_id: str,
    finding_update: FindingUpdate,
    request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a finding.
    
    This endpoint allows updating finding fields including status.
    Status transitions are validated by the backend to ensure only valid
    transitions are allowed.
    
    Args:
        finding_id: Finding ID to update
        finding_update: Update data
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated finding object
        
    Raises:
        HTTPException: If finding not found, access denied, or update fails
    """
    try:
        # Validate finding exists
        existing_finding = await FindingService.get_finding_by_id(db, finding_id)
        
        if not existing_finding:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"Finding with ID {finding_id} not found"
                }
            )
        
        # Check modify permission
        AuthorizationService.require_finding_modify_permission(current_user, finding_id)
        
        # Extract client information for audit logging
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        request_id = get_request_id(request)
        
        # Attempt update with audit logging
        updated_finding = await FindingService.update_finding(
            db=db,
            finding_id=finding_id,
            finding_update=finding_update,
            user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id
        )
        
        if not updated_finding:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"Finding with ID {finding_id} not found"
                }
            )
        
        return FindingService.finding_to_schema(updated_finding)
        
    except ValueError as e:
        # Handle validation errors (e.g., invalid status transitions)
        logger.warning(f"Validation error updating finding {finding_id}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating finding {finding_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to update finding"
            }
        )


@router.get("/findings/{finding_id}/detection")
async def get_finding_detection(
    finding_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve the detection associated with a finding.
    
    Args:
        finding_id: Finding ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Detection object if found
        
    Raises:
        HTTPException: If finding not found, access denied, or no detection exists
    """
    try:
        # Validate finding exists
        finding = await FindingService.get_finding_by_id(db, finding_id)
        
        if not finding:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"Finding with ID {finding_id} not found"
                }
            )
        
        # Check view permission
        AuthorizationService.require_finding_view_permission(current_user, finding_id)
        
        detection = await FindingService.get_finding_detection(db, finding_id)
        
        if not detection:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"No detection found for finding {finding_id}"
                }
            )
        
        # Return detection as dict
        return {
            "id": detection.id,
            "detection_rule_id": detection.detection_rule_id,
            "event_id": detection.event_id,
            "detection_timestamp": detection.detection_timestamp,
            "severity": detection.severity,
            "confidence": detection.confidence,
            "rule_version": detection.rule_version,
            "detection_metadata": detection.detection_metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving detection for finding {finding_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to retrieve detection"
            }
        )


@router.get("/findings/{finding_id}/evidence")
async def get_finding_evidence(
    finding_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all evidence associated with a finding.
    
    Args:
        finding_id: Finding ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of evidence objects
        
    Raises:
        HTTPException: If finding not found or access denied
    """
    try:
        # Validate finding exists
        finding = await FindingService.get_finding_by_id(db, finding_id)
        
        if not finding:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"Finding with ID {finding_id} not found"
                }
            )
        
        # Check view permission
        AuthorizationService.require_finding_view_permission(current_user, finding_id)
        
        evidence_list = await FindingService.get_finding_evidence(db, finding_id)
        
        # Return evidence as list of dicts
        return [
            {
                "id": evidence.id,
                "finding_id": evidence.finding_id,
                "detection_id": evidence.detection_id,
                "event_id": evidence.event_id,
                "evidence_type": evidence.evidence_type,
                "evidence_content": evidence.evidence_content,
                "created_timestamp": evidence.created_timestamp
            }
            for evidence in evidence_list
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving evidence for finding {finding_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to retrieve evidence"
            }
        )