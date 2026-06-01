"""us6r7r_tiempos_reserva

Revision ID: b1f7a2c9d3e4
Revises: fa25e87da86c
Create Date: 2026-05-31 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1f7a2c9d3e4'
down_revision: Union[str, Sequence[str], None] = 'fa25e87da86c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('reservas', sa.Column('fecha_salida_real', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reservas', sa.Column('fecha_devolucion_real', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reservas', sa.Column('minutos_retraso', sa.Integer(), nullable=True))
    op.add_column('reservas', sa.Column('monto_penalizacion', sa.Numeric(precision=12, scale=2), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('reservas', 'monto_penalizacion')
    op.drop_column('reservas', 'minutos_retraso')
    op.drop_column('reservas', 'fecha_devolucion_real')
    op.drop_column('reservas', 'fecha_salida_real')
