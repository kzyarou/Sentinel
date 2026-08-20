from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Index, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class FindingStatus(str, enum.Enum):
    """Finding status enumeration."""
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class Finding(Base):
    """Represents a security-relevant result that can be investigated."""
    
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True)  # UUID
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Integer, nullable=False)  # 0-100
    status = Column(SQLEnum(FindingStatus), default=FindingStatus.OPEN, nullable=False, index=True)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    detection_id = Column(String, ForeignKey('detections.id'), nullable=True, index=True)
    finding_metadata = Column(JSON, nullable=True)  # Preserve detection information
    
    # Relationships
    detection = relationship("Detection", back_populates="finding")
    evidence = relationship("Evidence", back_populates="finding", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="finding", cascade="all, delete-orphan")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_findings_status_timestamp', 'status', 'created_timestamp'),
        Index('idx_findings_severity_timestamp', 'severity', 'created_timestamp'),
        Index('idx_findings_detection_status', 'detection_id', 'status'),
    )
