from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class AIAnalysisStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AIAnalysisBase(BaseModel):
    finding_id: str
    provider: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    prompt_version: Optional[str] = Field(None, max_length=50)
    analysis_result: Dict[str, Any]
    status: AIAnalysisStatus = AIAnalysisStatus.PENDING


class AIAnalysisCreate(AIAnalysisBase):
    pass


class AIAnalysisUpdate(BaseModel):
    finding_id: Optional[str] = None
    provider: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    prompt_version: Optional[str] = Field(None, max_length=50)
    analysis_result: Optional[Dict[str, Any]] = None
    status: Optional[AIAnalysisStatus] = None


class AIAnalysisInDBBase(AIAnalysisBase):
    id: str
    created_timestamp: datetime

    class Config:
        from_attributes = True


class AIAnalysis(AIAnalysisInDBBase):
    pass
