from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class DetectionBase(BaseModel):
    detection_rule_id: str
    event_id: str
    severity: str = Field(..., max_length=20)
    confidence: int = Field(..., ge=0, le=100)
    rule_version: str = Field(..., max_length=50)
    metadata: Optional[Dict[str, Any]] = None


class DetectionCreate(DetectionBase):
    pass


class DetectionUpdate(BaseModel):
    severity: Optional[str] = Field(None, max_length=20)
    confidence: Optional[int] = Field(None, ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None


class DetectionInDBBase(DetectionBase):
    id: str
    detection_timestamp: datetime

    class Config:
        from_attributes = True


class Detection(DetectionInDBBase):
    pass
