"""crear tabla push subscriptions

Revision ID: e7c4d2a9b801
Revises: d3b9c4e1f6a7
Create Date: 2026-06-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e7c4d2a9b801"
down_revision: Union[str, Sequence[str], None] = "d3b9c4e1f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("endpoint", sa.String(length=1024), nullable=False),
        sa.Column("p256dh", sa.String(length=255), nullable=False),
        sa.Column("auth", sa.String(length=255), nullable=False),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_push_subscriptions_usuario_id"),
        "push_subscriptions",
        ["usuario_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_push_subscriptions_endpoint"),
        "push_subscriptions",
        ["endpoint"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_push_subscriptions_endpoint"),
        table_name="push_subscriptions",
    )
    op.drop_index(
        op.f("ix_push_subscriptions_usuario_id"),
        table_name="push_subscriptions",
    )
    op.drop_table("push_subscriptions")
