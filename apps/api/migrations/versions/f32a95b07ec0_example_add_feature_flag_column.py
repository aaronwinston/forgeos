"""example add feature flag column

Revision ID: f32a95b07ec0
Revises: 27d829f2bca2
Create Date: 2026-04-26 23:57:02.140336

This is an example migration demonstrating how to add a new feature to the database.
In this case, we add a 'beta_features_enabled' column to the organization table
to allow organizations to opt into beta features.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f32a95b07ec0'
down_revision: Union[str, Sequence[str], None] = '27d829f2bca2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add beta features opt-in to organizations."""
    # Example: Add a new column to track beta feature adoption
    # op.add_column('organization', sa.Column('beta_features_enabled', sa.Boolean(), nullable=False, server_default='0'))
    # 
    # Note: This is commented out as a demonstration. When you want to add features:
    # 1. Uncomment the op.add_column line and modify as needed
    # 2. Run: alembic upgrade head
    # 3. Test that the migration applies correctly
    # 4. Commit the migration file to version control
    pass


def downgrade() -> None:
    """Downgrade schema: Remove beta features column."""
    # Example: Remove the column when downgrading
    # op.drop_column('organization', 'beta_features_enabled')
    pass
