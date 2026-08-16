"""add project tracking json

Revision ID: 7c9a2f0d8a41
Revises: 42c4308a4f09
Create Date: 2026-08-16 16:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c9a2f0d8a41"
down_revision: Union[str, Sequence[str], None] = "42c4308a4f09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("project", sa.Column("tracking_json", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("project", "tracking_json")
