from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class DetectionRuleBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: str = Field(..., max_length=100)
    severity: str = Field(..., max_length=20)
    version: str = Field(..., max_length=50)
    enabled: bool = True
    rule_definition: Dict[str, Any]


class DetectionRuleCreate(DetectionRuleBase):
    pass


class DetectionRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    severity: Optional[str] = Field(None, max_length=20)
    version: Optional[str] = Field(None, max_length=50)
    enabled: Optional[bool] = None
    rule_definition: Optional[Dict[str, Any]] = None


class DetectionRuleInDBBase(DetectionRuleBase):
    id: str
    created_timestamp: datetime
    updated_timestamp: datetime

    class Config:
        from_attributes = True


class DetectionRule(DetectionRuleInDBBase):
    pass
