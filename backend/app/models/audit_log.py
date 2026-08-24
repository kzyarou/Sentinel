from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Index, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class AuditActionCategory(str, enum.Enum):
    """Categories of audit actions."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    FINDING = "finding"
    DETECTION_RULE = "detection_rule"
    USER_ADMINISTRATION = "user_administration"
    SYSTEM = "system"


class AuditResult(str, enum.Enum):
    """Result of the audited action."""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


class AuditLog(Base):
    """Records security-sensitive user actions."""
    
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)  # UUID
    user_id = Column(String, ForeignKey('users.id'), nullable=True, index=True)  # Nullable for system events
    action = Column(String(100), nullable=False, index=True)
    action_category = Column(SQLEnum(AuditActionCategory), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    result = Column(SQLEnum(AuditResult), nullable=False, index=True, default=AuditResult.SUCCESS)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    request_id = Column(String(100), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    audit_metadata = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_logs_action_timestamp', 'action', 'timestamp'),
        Index('idx_audit_logs_resource_timestamp', 'resource_type', 'resource_id', 'timestamp'),
        Index('idx_audit_logs_category_timestamp', 'action_category', 'timestamp'),
        Index('idx_audit_logs_result_timestamp', 'result', 'timestamp'),
    )
