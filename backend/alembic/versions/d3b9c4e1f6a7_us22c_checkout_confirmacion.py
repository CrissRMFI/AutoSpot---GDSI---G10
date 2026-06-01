"""us22c_checkout_confirmacion

Revision ID: d3b9c4e1f6a7
Revises: c2a8b3d0e4f5
Create Date: 2026-05-31 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3b9c4e1f6a7'
down_revision: Union[str, Sequence[str], None] = 'c2a8b3d0e4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # checkouts_vehiculo pasa a 1:N (historial de intentos)
    op.drop_index(op.f('ix_checkouts_vehiculo_reserva_id'), table_name='checkouts_vehiculo')
    op.create_index(op.f('ix_checkouts_vehiculo_reserva_id'), 'checkouts_vehiculo', ['reserva_id'], unique=False)

    op.add_column(
        'checkouts_vehiculo',
        sa.Column('estado', sa.String(length=30), nullable=False, server_default='PENDIENTE_CONFIRMACION'),
    )
    op.add_column('checkouts_vehiculo', sa.Column('motivo_rechazo', sa.String(length=500), nullable=True))
    op.create_index(op.f('ix_checkouts_vehiculo_estado'), 'checkouts_vehiculo', ['estado'], unique=False)

    op.add_column('reservas', sa.Column('fecha_entrega_solicitada', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('reservas', 'fecha_entrega_solicitada')

    op.drop_index(op.f('ix_checkouts_vehiculo_estado'), table_name='checkouts_vehiculo')
    op.drop_column('checkouts_vehiculo', 'motivo_rechazo')
    op.drop_column('checkouts_vehiculo', 'estado')

    op.drop_index(op.f('ix_checkouts_vehiculo_reserva_id'), table_name='checkouts_vehiculo')
    op.create_index(op.f('ix_checkouts_vehiculo_reserva_id'), 'checkouts_vehiculo', ['reserva_id'], unique=True)
