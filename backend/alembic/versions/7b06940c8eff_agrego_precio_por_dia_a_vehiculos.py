"""agrego precio por dia a vehiculos

Revision ID: 7b06940c8eff
Revises: a8385185e33e
Create Date: 2026-05-12 10:29:10.347558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b06940c8eff"
down_revision: Union[str, Sequence[str], None] = "a8385185e33e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega la tarifa diaria definida por el propietario para US 5D."""
    op.add_column(
        "vehiculos",
        sa.Column(
            "precio_por_dia",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Elimina la tarifa diaria del vehículo."""
    op.drop_column("vehiculos", "precio_por_dia")
