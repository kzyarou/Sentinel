from sqlalchemy import Column, String, DateTime, Integer, JSON, Text, Boolean, Index, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class RuleCategory(str, enum.Enum):
    """Detection rule categories."""
    AUTHENTICATION = "AUTHENTICATION"
    ACCESS_CONTROL = "ACCESS_CONTROL"
    NETWORK = "NETWORK"
    PROCESS = "PROCESS"
    ENDPOINT = "ENDPOINT"
    SYSTEM = "SYSTEM"
    OTHER = "OTHER"


class RuleSeverity(str, enum.Enum):
    """Detection rule severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectionRule(Base):
    """Represents a versioned security detection definition."""
    
    __tablename__ = "detection_rules"
    
    id = Column(String, primary_key=True)  # UUID
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(SQLEnum(RuleCategory), nullable=False, index=True)
    severity = Column(SQLEnum(RuleSeverity), nullable=False)
    version = Column(String(50), nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    rule_definition = Column(JSON, nullable=False)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(255), nullable=True)  # User ID who created the rule
    updated_by = Column(String(255), nullable=True)  # User ID who last updated the rule
    
    # Relationships
    detections = relationship("Detection", back_populates="detection_rule")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_detection_rules_name_version', 'name', 'version', unique=True),
        Index('idx_detection_rules_category_enabled', 'category', 'enabled'),
        Index('idx_detection_rules_severity_enabled', 'severity', 'enabled'),
        Index('idx_detection_rules_enabled_version', 'enabled', 'version'),
    )
