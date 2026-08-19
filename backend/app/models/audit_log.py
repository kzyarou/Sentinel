from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class AuditLog(Base):
    """Records security-sensitive user actions."""
    
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)  # UUID
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    request_id = Column(String(100), nullable=True, index=True)
    audit_metadata = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_logs_action_timestamp', 'action', 'timestamp'),
        Index('idx_audit_logs_resource_timestamp', 'resource_type', 'resource_id', 'timestamp'),
    )
