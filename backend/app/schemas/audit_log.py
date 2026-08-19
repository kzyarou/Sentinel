from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class AuditLogBase(BaseModel):
    user_id: str
    action: str = Field(..., max_length=100)
    resource_type: str = Field(..., max_length=100)
    resource_id: Optional[str] = Field(None, max_length=255)
    request_id: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(BaseModel):
    user_id: Optional[str] = None
    action: Optional[str] = Field(None, max_length=100)
    resource_type: Optional[str] = Field(None, max_length=100)
    resource_id: Optional[str] = Field(None, max_length=255)
    request_id: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class AuditLogInDBBase(AuditLogBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLog(AuditLogInDBBase):
    pass
