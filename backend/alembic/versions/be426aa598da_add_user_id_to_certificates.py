"""add user_id to certificates

Revision ID: be426aa598da
Revises: ab378eb19230
Create Date: 2026-08-20 23:26:29.646554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'be426aa598da'
down_revision: Union[str, Sequence[str], None] = 'ab378eb19230'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('certificates', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False))
    op.create_index('ix_certificates_user_id', 'certificates', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_certificates_user_id', table_name='certificates')
    op.drop_column('certificates', 'user_id')
