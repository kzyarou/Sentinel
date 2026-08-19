from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class FindingStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class FindingBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    severity: str = Field(..., max_length=20)
    confidence: int = Field(..., ge=0, le=100)
    status: FindingStatus = FindingStatus.OPEN
    detection_id: Optional[str] = None


class FindingCreate(FindingBase):
    pass


class FindingUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    severity: Optional[str] = Field(None, max_length=20)
    confidence: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[FindingStatus] = None
    detection_id: Optional[str] = None


class FindingInDBBase(FindingBase):
    id: str
    created_timestamp: datetime
    updated_timestamp: datetime

    class Config:
        from_attributes = True


class Finding(FindingInDBBase):
    pass
