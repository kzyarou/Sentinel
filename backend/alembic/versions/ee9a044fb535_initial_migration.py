"""Initial migration

Revision ID: ee9a044fb535
Revises: 
Create Date: 2026-08-19 00:20:09.030084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee9a044fb535'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create a simple test table to verify migration system works
    op.create_table(
        'health_check',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('checked_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('health_check')
