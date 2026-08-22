from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class AIAnalysisStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AIAnalysisRequest(BaseModel):
    """Request schema for AI analysis."""
    force_refresh: bool = False


class AIAnalysisResponse(BaseModel):
    """Response schema for AI analysis."""
    id: str
    finding_id: str
    provider_name: str
    model_name: str
    model_version: Optional[str] = None
    summary: Optional[str] = None
    observed_indicators: List[Dict[str, Any]] = []
    possible_interpretation: Optional[str] = None
    recommended_investigation_steps: List[str] = []
    confidence_notes: Optional[str] = None
    risk_level: Optional[str] = None
    urgency: Optional[str] = None
    investigation_priority: Optional[str] = None
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
