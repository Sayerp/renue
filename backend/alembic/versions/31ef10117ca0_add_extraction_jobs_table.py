"""add extraction_jobs table

Revision ID: 31ef10117ca0
Revises: be426aa598da
Create Date: 2026-08-21 22:55:55.982711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '31ef10117ca0'
down_revision: Union[str, Sequence[str], None] = 'be426aa598da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'extraction_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('certificate_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('certificates.id'), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_extraction_jobs_user_id', 'extraction_jobs', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_extraction_jobs_user_id', table_name='extraction_jobs')
    op.drop_table('extraction_jobs')
