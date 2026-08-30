"""Add detection rule management enhancements

Revision ID: b79d17a
Revises: 099d65e
Create Date: 2026-08-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'sen19_add_detection_rule_management'
down_revision = 'fa26909f6904'  # Core data model migration
branch_labels = None
depends_on = None


def upgrade():
    """Add detection rule management enhancements."""
    
    # Add new columns to detection_rules table
    op.add_column('detection_rules', sa.Column('created_by', sa.String(255), nullable=True))
    op.add_column('detection_rules', sa.Column('updated_by', sa.String(255), nullable=True))
    
    # Remove unique constraint on name
    op.drop_index('ix_detection_rules_name', table_name='detection_rules')
    
    # Add composite unique constraint on name + version
    op.create_index(
        'ix_detection_rules_name_version',
        'detection_rules',
        ['name', 'version'],
        unique=True
    )
    
    # Add additional indexes for query optimization
    op.create_index(
        'ix_detection_rules_enabled_version',
        'detection_rules',
        ['enabled', 'version']
    )
    
    # Convert category and severity columns to use enum types
    # First, we need to convert existing data to use enum values
    op.execute("""
        UPDATE detection_rules 
        SET category = UPPER(category)
        WHERE category IS NOT NULL
    """)
    
    op.execute("""
        UPDATE detection_rules 
        SET severity = UPPER(severity)
        WHERE severity IS NOT NULL
    """)
    
    # Alter columns to use enum types
    with op.batch_alter_table('detection_rules') as batch_op:
        batch_op.alter_column(
            'category',
            existing_type=sa.String(100),
            type_=sa.Enum(
                'AUTHENTICATION',
                'ACCESS_CONTROL',
                'NETWORK',
                'PROCESS',
                'ENDPOINT',
                'SYSTEM',
                'OTHER',
                name='rulecategory'
            ),
            nullable=False
        )
        batch_op.alter_column(
            'severity',
            existing_type=sa.String(20),
            type_=sa.Enum(
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL',
                name='ruleseverity'
            ),
            nullable=False
        )


def downgrade():
    """Remove detection rule management enhancements."""
    
    # Revert enum columns back to string types
    with op.batch_alter_table('detection_rules') as batch_op:
        batch_op.alter_column(
            'category',
            existing_type=sa.Enum(
                'AUTHENTICATION',
                'ACCESS_CONTROL',
                'NETWORK',
                'PROCESS',
                'ENDPOINT',
                'SYSTEM',
                'OTHER',
                name='rulecategory'
            ),
            type_=sa.String(100),
            nullable=False
        )
        batch_op.alter_column(
            'severity',
            existing_type=sa.Enum(
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL',
                name='ruleseverity'
            ),
            type_=sa.String(20),
            nullable=False
        )
    
    # Remove new indexes
    op.drop_index('ix_detection_rules_enabled_version', table_name='detection_rules')
    op.drop_index('ix_detection_rules_name_version', table_name='detection_rules')
    
    # Restore unique constraint on name
    op.create_index(
        'ix_detection_rules_name',
        'detection_rules',
        ['name'],
        unique=True
    )
    
    # Remove new columns
    op.drop_column('detection_rules', 'updated_by')
    op.drop_column('detection_rules', 'created_by')