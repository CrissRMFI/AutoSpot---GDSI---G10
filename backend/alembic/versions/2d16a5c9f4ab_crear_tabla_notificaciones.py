"""crear tabla notificaciones

Revision ID: 2d16a5c9f4ab
Revises: a98d562147ec
Create Date: 2026-05-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2d16a5c9f4ab"
down_revision: Union[str, Sequence[str], None] = "a98d562147ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notificaciones",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("titulo", sa.String(length=140), nullable=False),
        sa.Column("mensaje", sa.String(length=500), nullable=False),
        sa.Column("recurso_tipo", sa.String(length=50), nullable=True),
        sa.Column("recurso_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vista_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notificaciones_usuario_id"),
        "notificaciones",
        ["usuario_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_notificaciones_usuario_id"), table_name="notificaciones")
    op.drop_table("notificaciones")
