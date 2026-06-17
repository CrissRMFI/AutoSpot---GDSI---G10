"""
Esquemas Pydantic — US 16C: Gestion de incidentes y reportes de siniestros en curso.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

class ReportePayloadSchema(BaseModel):
    """Payload HTTP para registrar un reporte de incidente.

    Nota: `reserva_id` se recibe como path parameter en el endpoint,
    por lo que no es requerido en el body.
    """

    descripcion: str = Field(
        ...,
        max_length=1000,
        description="Texto libre del conductor describiendo el problema.",
    )
    url_foto_adjuntada: str | None = Field(
        None,
        max_length=255,
        description="URL de la foto adjuntada por el conductor (opcional).",
    )

class ReporteResponseSchema(BaseModel):
    """Respuesta pública de un reporte registrado."""

    id: uuid.UUID
    reserva_id: uuid.UUID
    conductor_id: uuid.UUID
    vehiculo_id: uuid.UUID
    descripcion: str
    url_foto_adjuntada: str | None
    created_at: datetime

    model_config = {"from_attributes": True}