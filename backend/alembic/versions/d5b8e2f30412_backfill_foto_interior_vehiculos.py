"""backfill_foto_interior_vehiculos

Inserta una foto INTERIOR placeholder para cada vehículo existente que aún
no la tenga. Necesario tras hacer INTERIOR un lado obligatorio (sprint 2):
los autos cargados antes del cambio quedarían con 4 fotos y romperían el
flujo de Modificar vehículo.

Revision ID: d5b8e2f30412
Revises: c7a9d1f0e201
Create Date: 2026-05-20 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d5b8e2f30412"
down_revision: Union[str, Sequence[str], None] = "c7a9d1f0e201"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


URL_INTERIOR_PLACEHOLDER = (
    "https://res.cloudinary.com/developmentcrissroldan/image/upload/"
    "v1779331974/autospot/vehiculos/Toyota-Corolla-2025_interior_rdk3pp.jpg"
)


def upgrade() -> None:
    """Inserta foto INTERIOR para los vehículos que no la tienen."""
    op.execute(
        f"""
        INSERT INTO fotos_vehiculo (id, vehiculo_id, lado, url, formato, tamanio_bytes, created_at)
        SELECT
            gen_random_uuid(),
            v.id,
            'INTERIOR',
            '{URL_INTERIOR_PLACEHOLDER}',
            'jpg',
            100000,
            NOW()
        FROM vehiculos v
        WHERE NOT EXISTS (
            SELECT 1 FROM fotos_vehiculo f
            WHERE f.vehiculo_id = v.id AND f.lado = 'INTERIOR'
        );
        """
    )


def downgrade() -> None:
    """Elimina solo las fotos INTERIOR insertadas con la URL placeholder."""
    op.execute(
        f"""
        DELETE FROM fotos_vehiculo
        WHERE lado = 'INTERIOR' AND url = '{URL_INTERIOR_PLACEHOLDER}';
        """
    )
