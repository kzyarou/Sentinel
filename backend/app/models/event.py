from sqlalchemy import Column, String, DateTime, JSON, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Event(Base):
    """Represents normalized telemetry received by Sentinel."""
    
    __tablename__ = "events"
    
    id = Column(String, primary_key=True)  # UUID
    event_type = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    host = Column(String(255), nullable=True, index=True)
    user = Column(String(255), nullable=True, index=True)
    normalized_data = Column(JSON, nullable=True)
    raw_data = Column(Text, nullable=True)  # Original event data
    ingestion_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    detections = relationship("Detection", back_populates="event")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_events_source_timestamp', 'source', 'timestamp'),
        Index('idx_events_type_timestamp', 'event_type', 'timestamp'),
        Index('idx_events_host_timestamp', 'host', 'timestamp'),
    )
