from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Detection(Base):
    """Represents a rule or analytic condition that matched an event or group of events."""
    
    __tablename__ = "detections"
    
    id = Column(String, primary_key=True)  # UUID
    detection_rule_id = Column(String, ForeignKey('detection_rules.id'), nullable=False, index=True)
    event_id = Column(String, ForeignKey('events.id'), nullable=False, index=True)
    detection_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Integer, nullable=False)  # 0-100
    rule_version = Column(String(50), nullable=False, index=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    detection_rule = relationship("DetectionRule", back_populates="detections")
    event = relationship("Event", back_populates="detections")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_detections_rule_timestamp', 'detection_rule_id', 'detection_timestamp'),
        Index('idx_detections_severity_timestamp', 'severity', 'detection_timestamp'),
    )
