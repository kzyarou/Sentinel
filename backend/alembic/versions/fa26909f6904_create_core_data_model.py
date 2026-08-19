"""Create core data model

Revision ID: fa26909f6904
Revises: ee9a044fb535
Create Date: 2026-08-19 02:54:40.452552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa26909f6904'
down_revision: Union[str, Sequence[str], None] = 'ee9a044fb535'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the initial test table
    op.drop_table('health_check')
    
    # Create detection_rules table
    op.create_table(
        'detection_rules',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('rule_definition', sa.JSON(), nullable=False),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.Index('idx_detection_rules_category_enabled', 'category', 'enabled'),
        sa.Index('idx_detection_rules_severity_enabled', 'severity', 'enabled'),
    )
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=True),
        sa.Column('user', sa.String(length=255), nullable=True),
        sa.Column('normalized_data', sa.JSON(), nullable=True),
        sa.Column('raw_data', sa.Text(), nullable=True),
        sa.Column('ingestion_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_events_source_timestamp', 'source', 'timestamp'),
        sa.Index('idx_events_type_timestamp', 'event_type', 'timestamp'),
        sa.Index('idx_events_host_timestamp', 'host', 'timestamp'),
        sa.Index('ix_events_event_type'),
        sa.Index('ix_events_host'),
        sa.Index('ix_events_source'),
        sa.Index('ix_events_timestamp'),
        sa.Index('ix_events_user'),
    )
    
    # Create detections table
    op.create_table(
        'detections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('detection_rule_id', sa.String(), nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('detection_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('rule_version', sa.String(length=50), nullable=False),
        sa.Column('detection_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['detection_rule_id'], ['detection_rules.id']),
        sa.ForeignKeyConstraint(['event_id'], ['events.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_detections_rule_timestamp', 'detection_rule_id', 'detection_timestamp'),
        sa.Index('idx_detections_severity_timestamp', 'severity', 'detection_timestamp'),
        sa.Index('ix_detections_detection_rule_id'),
        sa.Index('ix_detections_detection_timestamp'),
        sa.Index('ix_detections_event_id'),
        sa.Index('ix_detections_rule_version'),
        sa.Index('ix_detections_severity'),
    )
    
    # Create findings table
    op.create_table(
        'findings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('OPEN', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE', name='findingstatus', create_type=True), nullable=False, server_default='OPEN'),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('detection_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['detection_id'], ['detections.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_findings_severity_timestamp', 'severity', 'created_timestamp'),
        sa.Index('idx_findings_status_timestamp', 'status', 'created_timestamp'),
        sa.Index('ix_findings_confidence'),
        sa.Index('ix_findings_created_timestamp'),
        sa.Index('ix_findings_detection_id'),
        sa.Index('ix_findings_severity'),
        sa.Index('ix_findings_status'),
    )
    
    # Create evidence table
    op.create_table(
        'evidence',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('finding_id', sa.String(), nullable=False),
        sa.Column('event_id', sa.String(), nullable=True),
        sa.Column('evidence_type', sa.String(length=100), nullable=False),
        sa.Column('evidence_content', sa.JSON(), nullable=False),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id']),
        sa.ForeignKeyConstraint(['finding_id'], ['findings.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_evidence_finding_timestamp', 'finding_id', 'created_timestamp'),
        sa.Index('idx_evidence_type_timestamp', 'evidence_type', 'created_timestamp'),
        sa.Index('ix_evidence_created_timestamp'),
        sa.Index('ix_evidence_event_id'),
        sa.Index('ix_evidence_evidence_type'),
        sa.Index('ix_evidence_finding_id'),
    )
    
    # Create ai_analyses table
    op.create_table(
        'ai_analyses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('finding_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('prompt_version', sa.String(length=50), nullable=True),
        sa.Column('analysis_result', sa.JSON(), nullable=False),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='aianalysisstatus', create_type=True), nullable=False, server_default='PENDING'),
        sa.ForeignKeyConstraint(['finding_id'], ['findings.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_ai_analyses_finding_timestamp', 'finding_id', 'created_timestamp'),
        sa.Index('idx_ai_analyses_status_timestamp', 'status', 'created_timestamp'),
        sa.Index('ix_ai_analyses_created_timestamp'),
        sa.Index('ix_ai_analyses_finding_id'),
        sa.Index('ix_ai_analyses_provider'),
        sa.Index('ix_ai_analyses_status'),
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', name='userrole', create_type=True), nullable=False, server_default='VIEWER'),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', name='userstatus', create_type=True), nullable=False, server_default='ACTIVE'),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
        sa.UniqueConstraint('username'),
        sa.Index('idx_users_role_status', 'role', 'status'),
        sa.Index('ix_users_external_id'),
        sa.Index('ix_users_role'),
        sa.Index('ix_users_status'),
        sa.Index('ix_users_username'),
    )
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('audit_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_audit_logs_action_timestamp', 'action', 'timestamp'),
        sa.Index('idx_audit_logs_resource_timestamp', 'resource_type', 'resource_id', 'timestamp'),
        sa.Index('idx_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        sa.Index('ix_audit_logs_action'),
        sa.Index('ix_audit_logs_request_id'),
        sa.Index('ix_audit_logs_resource_id'),
        sa.Index('ix_audit_logs_resource_type'),
        sa.Index('ix_audit_logs_timestamp'),
        sa.Index('ix_audit_logs_user_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order of creation
    op.drop_table('audit_logs')
    op.drop_table('users')
    op.drop_table('ai_analyses')
    op.drop_table('evidence')
    op.drop_table('findings')
    op.drop_table('detections')
    op.drop_table('events')
    op.drop_table('detection_rules')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS findingstatus')
    op.execute('DROP TYPE IF EXISTS aianalysisstatus')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS userstatus')
    
    # Recreate the initial test table
    op.create_table(
        'health_check',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('checked_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
