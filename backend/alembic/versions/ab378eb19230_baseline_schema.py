"""baseline schema

Revision ID: ab378eb19230
Revises: 
Create Date: 2026-08-19 22:33:39.087261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ab378eb19230'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'certificates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('course_name', sa.String(), nullable=True),
        sa.Column('completion_date', sa.String(), nullable=True),
        sa.Column('credits', sa.Numeric(), nullable=True),
    )
    op.create_index('ix_certificates_provider', 'certificates', ['provider'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_certificates_provider', table_name='certificates')
    op.drop_table('certificates')
