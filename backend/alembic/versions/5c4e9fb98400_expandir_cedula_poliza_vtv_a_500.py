"""expandir cedula, poliza y vtv a 500 chars (Cloudinary URLs)

Revision ID: 5c4e9fb98400
Revises: 8a46a9a3e6d0
Create Date: 2026-05-20 02:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5c4e9fb98400"
down_revision: Union[str, Sequence[str], None] = "8a46a9a3e6d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: ampliar columnas para almacenar URLs de Cloudinary."""
    op.alter_column(
        "vehiculos",
        "cedula",
        existing_type=sa.String(length=50),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
    op.alter_column(
        "vehiculos",
        "poliza",
        existing_type=sa.String(length=50),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
    op.alter_column(
        "vehiculos",
        "vtv",
        existing_type=sa.String(length=50),
        type_=sa.String(length=500),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "vehiculos",
        "vtv",
        existing_type=sa.String(length=500),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "vehiculos",
        "poliza",
        existing_type=sa.String(length=500),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "vehiculos",
        "cedula",
        existing_type=sa.String(length=500),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
