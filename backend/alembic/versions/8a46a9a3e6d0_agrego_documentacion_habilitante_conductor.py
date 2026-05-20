"""agrego documentacion habilitante del conductor (US 1C)

Revision ID: 8a46a9a3e6d0
Revises: 7beb62ff66be
Create Date: 2026-05-20 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8a46a9a3e6d0"
down_revision: Union[str, Sequence[str], None] = "7beb62ff66be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "documentacion_habilitante_conductor",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("numero_licencia", sa.String(length=30), nullable=False),
        sa.Column("categoria", sa.String(length=10), nullable=False),
        sa.Column("fecha_emision", sa.Date(), nullable=False),
        sa.Column("fecha_vencimiento", sa.Date(), nullable=False),
        sa.Column("foto_licencia_frente_url", sa.String(length=500), nullable=False),
        sa.Column("foto_licencia_dorso_url", sa.String(length=500), nullable=False),
        sa.Column("estado_validacion", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "usuario_id",
            name="uq_documentacion_habilitante_conductor_usuario_id",
        ),
    )
    op.create_index(
        op.f("ix_documentacion_habilitante_conductor_usuario_id"),
        "documentacion_habilitante_conductor",
        ["usuario_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_documentacion_habilitante_conductor_usuario_id"),
        table_name="documentacion_habilitante_conductor",
    )
    op.drop_table("documentacion_habilitante_conductor")
