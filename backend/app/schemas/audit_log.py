from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class AuditActionCategory(str, Enum):
    """Categories of audit actions for classification."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    FINDING = "finding"
    DETECTION_RULE = "detection_rule"
    USER_ADMINISTRATION = "user_administration"
    SYSTEM = "system"


class AuditResult(str, Enum):
    """Result status of audit events."""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


class AuditLogBase(BaseModel):
    """Base audit log schema."""
    action: str = Field(..., max_length=100)
    action_category: AuditActionCategory
    resource_type: str = Field(..., max_length=100)
    resource_id: Optional[str] = Field(None, max_length=255)
    result: AuditResult = AuditResult.SUCCESS
    request_id: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit logs."""
    user_id: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    """Schema for audit log responses."""
    id: str
    user_id: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AuditLogStats(BaseModel):
    """Schema for audit log statistics."""
    total_count: int
    category_stats: Dict[str, int]
    result_stats: Dict[str, int]
    last_24h_count: int