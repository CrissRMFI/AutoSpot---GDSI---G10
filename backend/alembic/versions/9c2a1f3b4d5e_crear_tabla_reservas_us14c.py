"""crear tabla reservas us14c

Revision ID: 9c2a1f3b4d5e
Revises: 2d16a5c9f4ab
Create Date: 2026-05-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c2a1f3b4d5e"
down_revision: Union[str, Sequence[str], None] = "2d16a5c9f4ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "reservas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("vehiculo_id", sa.Uuid(), nullable=False),
        sa.Column("conductor_id", sa.Uuid(), nullable=False),
        sa.Column("codigo", sa.String(length=32), nullable=False),
        sa.Column("codigo_verificado_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estado", sa.String(length=50), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("fecha_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estacion_retiro", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conductor_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["vehiculo_id"], ["vehiculos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
    )
    op.create_index(op.f("ix_reservas_codigo"), "reservas", ["codigo"], unique=True)
    op.create_index(op.f("ix_reservas_conductor_id"), "reservas", ["conductor_id"], unique=False)
    op.create_index(op.f("ix_reservas_estado"), "reservas", ["estado"], unique=False)
    op.create_index(op.f("ix_reservas_vehiculo_id"), "reservas", ["vehiculo_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_reservas_vehiculo_id"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_estado"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_conductor_id"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_codigo"), table_name="reservas")
    op.drop_table("reservas")
