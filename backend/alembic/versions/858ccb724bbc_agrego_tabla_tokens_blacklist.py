"""agrego tabla tokens blacklist

Revision ID: 858ccb724bbc
Revises: 7b06940c8eff
Create Date: 2026-05-13 00:55:55.274520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "858ccb724bbc"
down_revision: Union[str, Sequence[str], None] = "7b06940c8eff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tokens_blacklist",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("blacklisted_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_tokens_blacklist_jti"),
        "tokens_blacklist",
        ["jti"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_tokens_blacklist_jti"),
        table_name="tokens_blacklist",
    )

    op.drop_table("tokens_blacklist")