from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class DetectionRuleBase(BaseModel):
    name: str = Field(..., max_length=255, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    category: RuleCategory = Field(..., description="Rule category")
    severity: RuleSeverity = Field(..., description="Rule severity")
    version: str = Field(..., max_length=50, description="Rule version")
    enabled: bool = Field(default=True, description="Whether the rule is enabled")
    rule_definition: Dict[str, Any] = Field(..., description="Rule definition in structured format")


class DetectionRuleCreate(DetectionRuleBase):
    pass


class DetectionRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    category: Optional[RuleCategory] = Field(None, description="Rule category")
    severity: Optional[RuleSeverity] = Field(None, description="Rule severity")
    version: Optional[str] = Field(None, max_length=50, description="Rule version")
    enabled: Optional[bool] = Field(None, description="Whether the rule is enabled")
    rule_definition: Optional[Dict[str, Any]] = Field(None, description="Rule definition in structured format")


class DetectionRuleInDBBase(DetectionRuleBase):
    id: str
    created_timestamp: datetime
    updated_timestamp: datetime
    created_by: Optional[str] = Field(None, description="User ID who created the rule")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the rule")

    class Config:
        from_attributes = True


class DetectionRule(DetectionRuleInDBBase):
    pass
