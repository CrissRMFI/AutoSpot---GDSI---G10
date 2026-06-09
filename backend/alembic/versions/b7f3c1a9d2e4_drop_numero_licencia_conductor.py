"""drop numero_licencia de documentacion_habilitante_conductor

En Argentina el número de la licencia coincide con el DNI, por lo que el campo
separado `numero_licencia` no aporta y se elimina del modelo de documentación
habilitante del conductor.

Revision ID: b7f3c1a9d2e4
Revises: f8e2d1c3b4a5
Create Date: 2026-06-09
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7f3c1a9d2e4"
down_revision = "f8e2d1c3b4a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("documentacion_habilitante_conductor", "numero_licencia")


def downgrade() -> None:
    op.add_column(
        "documentacion_habilitante_conductor",
        sa.Column("numero_licencia", sa.String(length=30), nullable=True),
    )
