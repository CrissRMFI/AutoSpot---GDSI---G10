"""agrego_rol_a_usuarios

Revision ID: c7a9d1f0e201
Revises: 154665f8e23e
Create Date: 2026-05-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7a9d1f0e201"
down_revision: Union[str, Sequence[str], None] = "154665f8e23e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega columna rol a usuarios con default CLIENTE para filas existentes."""
    op.add_column(
        "usuarios",
        sa.Column(
            "rol",
            sa.String(length=20),
            nullable=False,
            server_default="CLIENTE",
        ),
    )


def downgrade() -> None:
    """Elimina columna rol de usuarios."""
    op.drop_column("usuarios", "rol")
