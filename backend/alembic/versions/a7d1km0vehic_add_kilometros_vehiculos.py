"""add kilometros a vehiculos

Revision ID: a7d1km0vehic
Revises: c1d2e3f4a5b6
Create Date: 2026-06-21 00:00:00.000000

"""
from typing import Sequence, Union
from datetime import datetime
import random

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7d1km0vehic"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _km_realista(anio, anio_actual: int) -> int:
    """Kilometraje realista según la antigüedad (~12k–18k/año + ruido)."""
    if not anio:
        return random.randint(20_000, 80_000)
    edad = max(0, anio_actual - int(anio))
    if edad == 0:
        return random.randint(50, 2_000)
    return edad * random.randint(12_000, 18_000) + random.randint(0, 6_000)


def upgrade() -> None:
    """
    Agrega la columna kilometros (odómetro) a vehiculos y backfillea un
    kilometraje realista en los autos existentes (solo donde es NULL).

    Esto se ejecuta una sola vez por base de datos (alembic registra la
    revisión), e idempotente: no pisa valores ya cargados.
    """
    op.add_column(
        "vehiculos",
        sa.Column("kilometros", sa.Integer(), nullable=True),
    )

    conn = op.get_bind()
    filas = conn.execute(
        sa.text("SELECT id, anio FROM vehiculos WHERE kilometros IS NULL")
    ).fetchall()
    anio_actual = datetime.now().year
    for fila in filas:
        conn.execute(
            sa.text("UPDATE vehiculos SET kilometros = :km WHERE id = :id"),
            {"km": _km_realista(fila.anio, anio_actual), "id": fila.id},
        )


def downgrade() -> None:
    op.drop_column("vehiculos", "kilometros")
