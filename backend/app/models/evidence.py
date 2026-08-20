from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Evidence(Base):
    """Represents information supporting a detection or finding."""
    
    __tablename__ = "evidence"
    
    id = Column(String, primary_key=True)  # UUID
    finding_id = Column(String, ForeignKey('findings.id'), nullable=True, index=True)
    detection_id = Column(String, ForeignKey('detections.id'), nullable=True, index=True)
    event_id = Column(String, ForeignKey('events.id'), nullable=True, index=True)
    evidence_type = Column(String(100), nullable=False, index=True)
    evidence_content = Column(JSON, nullable=False)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    finding = relationship("Finding", back_populates="evidence")
    detection = relationship("Detection", back_populates="evidence")
    event = relationship("Event", backref="evidence")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_evidence_finding_timestamp', 'finding_id', 'created_timestamp'),
        Index('idx_evidence_detection_timestamp', 'detection_id', 'created_timestamp'),
        Index('idx_evidence_type_timestamp', 'evidence_type', 'created_timestamp'),
    )
