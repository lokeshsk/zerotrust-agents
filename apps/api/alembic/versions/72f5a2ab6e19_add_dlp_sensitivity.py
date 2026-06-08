"""add dlp sensitivity

Revision ID: 72f5a2ab6e19
Revises: 72f5a2ab6e18
Create Date: 2026-06-08 17:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72f5a2ab6e19'
down_revision: Union[str, Sequence[str], None] = '72f5a2ab6e18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tenants', sa.Column('dlp_sensitivity', sa.String(), server_default='high', nullable=True))
    op.add_column('tenants', sa.Column('mcp_upstream_url', sa.String(), server_default='http://localhost:8080', nullable=True))


def downgrade() -> None:
    op.drop_column('tenants', 'mcp_upstream_url')
    op.drop_column('tenants', 'dlp_sensitivity')
