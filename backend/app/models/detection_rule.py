from sqlalchemy import Column, String, DateTime, Integer, JSON, Text, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class DetectionRule(Base):
    """Represents a versioned security detection definition."""
    
    __tablename__ = "detection_rules"
    
    id = Column(String, primary_key=True)  # UUID
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    version = Column(String(50), nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    rule_definition = Column(JSON, nullable=False)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    detections = relationship("Detection", back_populates="detection_rule")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_detection_rules_category_enabled', 'category', 'enabled'),
        Index('idx_detection_rules_severity_enabled', 'severity', 'enabled'),
    )
