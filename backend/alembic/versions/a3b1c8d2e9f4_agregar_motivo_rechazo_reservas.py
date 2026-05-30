"""agregar motivo_rechazo a reservas

Revision ID: a3b1c8d2e9f4
Revises: 9c2a1f3b4d5e
Create Date: 2026-05-29 01:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3b1c8d2e9f4"
down_revision: Union[str, Sequence[str], None] = "9c2a1f3b4d5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "reservas",
        sa.Column("motivo_rechazo", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("reservas", "motivo_rechazo")
