from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Index, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class AIAnalysisStatus(str, enum.Enum):
    """AI analysis status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AIAnalysis(Base):
    """Represents advisory analysis generated from an existing finding."""
    
    __tablename__ = "ai_analyses"
    
    id = Column(String, primary_key=True)  # UUID
    finding_id = Column(String, ForeignKey('findings.id'), nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    prompt_version = Column(String(50), nullable=True)
    analysis_result = Column(JSON, nullable=False)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    status = Column(SQLEnum(AIAnalysisStatus), default=AIAnalysisStatus.PENDING, nullable=False, index=True)
    
    # Relationships
    finding = relationship("Finding", back_populates="ai_analyses")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_ai_analyses_finding_timestamp', 'finding_id', 'created_timestamp'),
        Index('idx_ai_analyses_status_timestamp', 'status', 'created_timestamp'),
    )
