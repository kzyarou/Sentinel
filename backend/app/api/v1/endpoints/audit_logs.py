from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.audit_log import AuditLog, AuditActionCategory, AuditResult
from app.api.v1.endpoints.dependencies import get_current_user
from app.models.user import User
from app.core.authorization import AuthorizationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    action_category: Optional[str] = Query(None, description="Filter by action category"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    result: Optional[str] = Query(None, description="Filter by result (success, failure, error)"),
    request_id: Optional[str] = Query(None, description="Filter by request ID"),
    start_time: Optional[str] = Query(None, description="Start time (ISO 8601)"),
    end_time: Optional[str] = Query(None, description="End time (ISO 8601)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve audit logs with optional filtering.
    
    This endpoint provides access to security audit logs for security monitoring
    and investigation. Access is restricted to administrators only.
    
    Args:
        skip: Number of results to skip (pagination)
        limit: Maximum number of results to return
        user_id: Filter by user ID
        action: Filter by action
        action_category: Filter by action category
        resource_type: Filter by resource type
        resource_id: Filter by resource ID
        result: Filter by result
        request_id: Filter by request ID
        start_time: Start time for time range filter
        end_time: End time for time range filter
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of audit logs matching the criteria
        
    Raises:
        HTTPException: If user is not authorized or query fails
    """
    try:
        # Require admin access for audit logs
        AuthorizationService.require_audit_log_permission(current_user)
        
        # Build query with filters
        query = select(AuditLog)
        
        # Apply filters
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        
        if action:
            query = query.where(AuditLog.action == action)
        
        if action_category:
            try:
                category = AuditActionCategory(action_category)
                query = query.where(AuditLog.action_category == category)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_category",
                        "message": f"Invalid action category: {action_category}"
                    }
                )
        
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        
        if resource_id:
            query = query.where(AuditLog.resource_id == resource_id)
        
        if result:
            try:
                result_enum = AuditResult(result)
                query = query.where(AuditLog.result == result_enum)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_result",
                        "message": f"Invalid result: {result}"
                    }
                )
        
        if request_id:
            query = query.where(AuditLog.request_id == request_id)
        
        # Time range filtering
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time)
                query = query.where(AuditLog.timestamp >= start_dt)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_time_format",
                        "message": "Invalid start_time format. Use ISO 8601 format."
                    }
                )
        
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time)
                query = query.where(AuditLog.timestamp <= end_dt)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_time_format",
                        "message": "Invalid end_time format. Use ISO 8601 format."
                    }
                )
        
        # Order by timestamp descending (most recent first)
        query = query.order_by(AuditLog.timestamp.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        audit_logs = result.scalars().all()
        
        # Convert to response format
        response_data = []
        for log in audit_logs:
            response_data.append({
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "action_category": log.action_category.value if log.action_category else None,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "request_id": log.request_id,
                "result": log.result.value if log.result else None,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "metadata": log.audit_metadata
            })
        
        logger.info(f"Retrieved {len(response_data)} audit logs for user {current_user.id}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to retrieve audit logs"
            }
        )


@router.get("/audit-logs/stats")
async def get_audit_log_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get audit log statistics.
    
    Provides summary statistics about audit logs for monitoring and analysis.
    Access is restricted to administrators only.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dictionary with audit log statistics
        
    Raises:
        HTTPException: If user is not authorized or query fails
    """
    try:
        # Require admin access for audit log statistics
        AuthorizationService.require_audit_log_permission(current_user)
        
        # Get total count
        total_count = await db.execute(select(AuditLog).count())
        total = total_count.scalar()
        
        # Get count by action category
        category_stats = {}
        for category in AuditActionCategory:
            count_result = await db.execute(
                select(AuditLog).where(AuditLog.action_category == category).count()
            )
            category_stats[category.value] = count_result.scalar()
        
        # Get count by result
        result_stats = {}
        for result in AuditResult:
            count_result = await db.execute(
                select(AuditLog).where(AuditLog.result == result).count()
            )
            result_stats[result.value] = count_result.scalar()
        
        # Get count for last 24 hours
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_count = await db.execute(
            select(AuditLog).where(AuditLog.timestamp >= last_24h).count()
        )
        recent = recent_count.scalar()
        
        logger.info(f"Retrieved audit log statistics for user {current_user.id}")
        
        return {
            "total_count": total,
            "category_stats": category_stats,
            "result_stats": result_stats,
            "last_24h_count": recent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit log statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to retrieve audit log statistics"
            }
        )