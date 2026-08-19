from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class EvidenceBase(BaseModel):
    finding_id: str
    event_id: Optional[str] = None
    evidence_type: str = Field(..., max_length=100)
    evidence_content: Dict[str, Any]


class EvidenceCreate(EvidenceBase):
    pass


class EvidenceUpdate(BaseModel):
    finding_id: Optional[str] = None
    event_id: Optional[str] = None
    evidence_type: Optional[str] = Field(None, max_length=100)
    evidence_content: Optional[Dict[str, Any]] = None


class EvidenceInDBBase(EvidenceBase):
    id: str
    created_timestamp: datetime

    class Config:
        from_attributes = True


class Evidence(EvidenceInDBBase):
    pass
