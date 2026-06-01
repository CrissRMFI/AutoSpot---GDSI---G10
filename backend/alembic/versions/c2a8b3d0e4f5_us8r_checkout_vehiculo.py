"""us8r_checkout_vehiculo

Revision ID: c2a8b3d0e4f5
Revises: b1f7a2c9d3e4
Create Date: 2026-05-31 19:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2a8b3d0e4f5'
down_revision: Union[str, Sequence[str], None] = 'b1f7a2c9d3e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('checkouts_vehiculo',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('reserva_id', sa.Uuid(), nullable=False),
    sa.Column('recepcionista_id', sa.Uuid(), nullable=False),
    sa.Column('nivel_combustible', sa.String(length=20), nullable=False),
    sa.Column('kilometraje_actual', sa.Integer(), nullable=False),
    sa.Column('esta_limpio', sa.Boolean(), nullable=False),
    sa.Column('tiene_danios', sa.Boolean(), nullable=False),
    sa.Column('descripcion_danios', sa.String(length=500), nullable=True),
    sa.Column('url_foto_frente', sa.String(length=255), nullable=False),
    sa.Column('url_foto_trasera', sa.String(length=255), nullable=False),
    sa.Column('url_foto_lateral_izq', sa.String(length=255), nullable=False),
    sa.Column('url_foto_lateral_der', sa.String(length=255), nullable=False),
    sa.Column('url_foto_panel', sa.String(length=255), nullable=False),
    sa.Column('urls_fotos_danios', sa.JSON(), nullable=False),
    sa.Column('url_foto_extra', sa.String(length=255), nullable=True),
    sa.Column('notas_adicionales', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['recepcionista_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['reserva_id'], ['reservas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checkouts_vehiculo_recepcionista_id'), 'checkouts_vehiculo', ['recepcionista_id'], unique=False)
    op.create_index(op.f('ix_checkouts_vehiculo_reserva_id'), 'checkouts_vehiculo', ['reserva_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_checkouts_vehiculo_reserva_id'), table_name='checkouts_vehiculo')
    op.drop_index(op.f('ix_checkouts_vehiculo_recepcionista_id'), table_name='checkouts_vehiculo')
    op.drop_table('checkouts_vehiculo')
