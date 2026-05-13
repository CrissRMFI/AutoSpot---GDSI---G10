"""Restore tokens_blacklist

Revision ID: af99ccbfc627
Revises: 88aa4fbb3a6a
Create Date: 2026-05-13 03:39:19.835553

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "af99ccbfc627"
down_revision: Union[str, Sequence[str], None] = "88aa4fbb3a6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # La tabla tokens_blacklist ya fue creada en la migración 858ccb724bbc.
    # Esta migración se conserva como no-op para mantener la cadena de Alembic.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # No se elimina tokens_blacklist acá porque pertenece a la migración 858ccb724bbc.
    pass