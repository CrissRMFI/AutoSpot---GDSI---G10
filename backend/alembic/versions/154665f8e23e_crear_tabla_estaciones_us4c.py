"""crear tabla estaciones us4c

Revision ID: 154665f8e23e
Revises: 5c4e9fb98400
Create Date: 2026-05-20 05:44:07.472776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '154665f8e23e'
down_revision: Union[str, Sequence[str], None] = '5c4e9fb98400'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'estaciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('direccion', sa.String(length=255), nullable=False),
        sa.Column('instrucciones_acceso', sa.String(length=1000), nullable=False),
        sa.Column('zona', sa.String(length=100), nullable=False),
        sa.Column('activa', sa.Boolean(), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_estaciones_id'), 'estaciones', ['id'], unique=False)

    op.bulk_insert(
        sa.table(
            'estaciones',
            sa.column('nombre', sa.String),
            sa.column('direccion', sa.String),
            sa.column('instrucciones_acceso', sa.String),
            sa.column('zona', sa.String),
            sa.column('activa', sa.Boolean),
            sa.column('imagen_url', sa.String),
        ),
        [
            {
                "nombre": "Spot Palermo Centro",
                "direccion": "Av. Santa Fe 3200",
                "instrucciones_acceso": "Ingreso por la rampa principal del subsuelo, sector A.",
                "zona": "Palermo",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot Recoleta",
                "direccion": "Junín 1700",
                "instrucciones_acceso": "Portón negro automático junto a la plaza. Tocar timbre AutoSpot.",
                "zona": "Recoleta",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot San Telmo",
                "direccion": "Defensa 800",
                "instrucciones_acceso": "Estacionamiento subterráneo. Presentar credencial digital en la cabina.",
                "zona": "San Telmo",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot Villa Crespo",
                "direccion": "Av. Corrientes 4500",
                "instrucciones_acceso": "Subir al primer piso por la rampa de vehículos, lockers al fondo.",
                "zona": "Villa Crespo",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot Belgrano Norte",
                "direccion": "Juramento 2100",
                "instrucciones_acceso": "Sector de cocheras reservadas AutoSpot en el nivel -1.",
                "zona": "Belgrano",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot Madero Premium",
                "direccion": "Juana Manso 900",
                "instrucciones_acceso": "Ingreso por la barrera principal; el personal de AutoSpot habilita el acceso al sector reservado.",
                "zona": "Puerto Madero",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot Caballito Centro",
                "direccion": "Av. Rivadavia 5100",
                "instrucciones_acceso": "Estacionamiento comercial, darsena 14 a 18 exclusivas.",
                "zona": "Caballito",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot Almagro",
                "direccion": "Medrano 400",
                "instrucciones_acceso": "Entrada peatonal por el pasillo lateral izquierdo.",
                "zona": "Almagro",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot Colegiales",
                "direccion": "Federico Lacroze 2800",
                "instrucciones_acceso": "Dejar el auto frente al tótem de AutoSpot y confirmar en la App.",
                "zona": "Colegiales",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot Chacarita",
                "direccion": "Olleros 3500",
                "instrucciones_acceso": "Portón gris corredizo. El código de apertura se genera al reservar.",
                "zona": "Chacarita",
                "activa": True,
                "imagen_url": None,
            },
            {
                "nombre": "Spot Palermo Soho",
                "direccion": "Honduras 4800",
                "instrucciones_acceso": "Estación temporalmente fuera de servicio por reformas.",
                "zona": "Palermo",
                "activa": False,
                "imagen_url": None,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_estaciones_id'), table_name='estaciones')
    op.drop_table('estaciones')
