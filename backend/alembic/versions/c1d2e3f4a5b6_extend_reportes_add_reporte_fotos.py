"""Extend reportes con campos de reporte critico y crea reporte_fotos

Revision ID: c1d2e3f4a5b6
Revises: ba20a786928a
Create Date: 2026-06-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'ba20a786928a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'reportes',
        sa.Column('tipo', sa.String(length=30), nullable=False, server_default='FALLA'),
    )
    op.add_column(
        'reportes',
        sa.Column('criticidad', sa.String(length=30), nullable=False, server_default='CRITICA'),
    )
    op.add_column(
        'reportes',
        sa.Column('estado', sa.String(length=30), nullable=False, server_default='ACTIVO'),
    )
    op.add_column(
        'reportes',
        sa.Column('resuelto_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'reportes',
        sa.Column('resuelto_por_id', sa.Uuid(), nullable=True),
    )
    op.add_column(
        'reportes',
        sa.Column('resolucion_descripcion', sa.String(length=1000), nullable=True),
    )
    op.create_index(op.f('ix_reportes_estado'), 'reportes', ['estado'], unique=False)
    op.create_foreign_key(
        'fk_reportes_resuelto_por_id_usuarios',
        'reportes',
        'usuarios',
        ['resuelto_por_id'],
        ['id'],
    )

    op.create_table(
        'reporte_fotos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('reporte_id', sa.Uuid(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('descripcion', sa.String(length=500), nullable=False),
        sa.Column('formato', sa.String(length=20), nullable=False),
        sa.Column('tamanio_bytes', sa.Integer(), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['reporte_id'], ['reportes.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_reporte_fotos_reporte_id'),
        'reporte_fotos',
        ['reporte_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_reporte_fotos_reporte_id'), table_name='reporte_fotos')
    op.drop_table('reporte_fotos')

    op.drop_constraint('fk_reportes_resuelto_por_id_usuarios', 'reportes', type_='foreignkey')
    op.drop_index(op.f('ix_reportes_estado'), table_name='reportes')
    op.drop_column('reportes', 'resolucion_descripcion')
    op.drop_column('reportes', 'resuelto_por_id')
    op.drop_column('reportes', 'resuelto_at')
    op.drop_column('reportes', 'estado')
    op.drop_column('reportes', 'criticidad')
    op.drop_column('reportes', 'tipo')
