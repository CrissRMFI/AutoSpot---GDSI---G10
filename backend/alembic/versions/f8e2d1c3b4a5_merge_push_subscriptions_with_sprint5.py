"""merge push subscriptions with sprint 5 heads

Revision ID: f8e2d1c3b4a5
Revises: 9f34c00c4301, e7c4d2a9b801
Create Date: 2026-06-08 00:00:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "f8e2d1c3b4a5"
down_revision: Union[str, Sequence[str], None] = (
    "9f34c00c4301",
    "e7c4d2a9b801",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge migration branches."""
    pass


def downgrade() -> None:
    """Split migration branches."""
    pass
