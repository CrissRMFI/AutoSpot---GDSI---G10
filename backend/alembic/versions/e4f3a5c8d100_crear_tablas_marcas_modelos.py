"""crear tablas marcas y modelos con seed inicial

Revision ID: e4f3a5c8d100
Revises: d5b8e2f30412
Create Date: 2026-05-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4f3a5c8d100"
down_revision: Union[str, Sequence[str], None] = "d5b8e2f30412"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SEED_CATALOGO = {
    "Toyota": ["Corolla", "Etios", "Hilux"],
    "Ford": ["Fiesta", "Focus", "Ranger"],
    "Volkswagen": ["Gol", "Polo", "Amarok"],
    "Chevrolet": ["Onix", "Cruze", "S10"],
    "Renault": ["Clio", "Sandero", "Kangoo"],
}


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "marcas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre", name="uq_marcas_nombre"),
    )
    op.create_index(op.f("ix_marcas_id"), "marcas", ["id"], unique=False)

    op.create_table(
        "modelos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("marca_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["marca_id"],
            ["marcas.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("marca_id", "nombre", name="uq_modelos_marca_nombre"),
    )
    op.create_index(op.f("ix_modelos_id"), "modelos", ["id"], unique=False)
    op.create_index(op.f("ix_modelos_marca_id"), "modelos", ["marca_id"], unique=False)

    # Seed inicial replicando el CATALOGO hardcodeado preexistente.
    marcas_table = sa.table(
        "marcas",
        sa.column("id", sa.Integer),
        sa.column("nombre", sa.String),
    )
    modelos_table = sa.table(
        "modelos",
        sa.column("id", sa.Integer),
        sa.column("marca_id", sa.Integer),
        sa.column("nombre", sa.String),
    )

    bind = op.get_bind()
    for nombre_marca, modelos in SEED_CATALOGO.items():
        resultado = bind.execute(
            marcas_table.insert().values(nombre=nombre_marca).returning(marcas_table.c.id)
        )
        marca_id = resultado.scalar()
        bind.execute(
            modelos_table.insert(),
            [{"marca_id": marca_id, "nombre": nombre} for nombre in modelos],
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_modelos_marca_id"), table_name="modelos")
    op.drop_index(op.f("ix_modelos_id"), table_name="modelos")
    op.drop_table("modelos")
    op.drop_index(op.f("ix_marcas_id"), table_name="marcas")
    op.drop_table("marcas")
