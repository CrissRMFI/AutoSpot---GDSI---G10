"""
Esquemas Pydantic — US 17C: Valoración cuantitativa del servicio.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ValoracionCreatePayloadSchema(BaseModel):
    """Payload HTTP para registrar una valoración."""

    reserva_id: uuid.UUID = Field(
        ...,
        description="ID de la reserva finalizada a valorar.",
    )
    puntaje: int = Field(
        ...,
        ge=1,
        le=5,
        description="Puntaje numérico del 1 al 5 (entero).",
    )


class ValoracionResponseSchema(BaseModel):
    """Respuesta pública de una valoración registrada."""

    id: uuid.UUID
    reserva_id: uuid.UUID
    conductor_id: uuid.UUID
    vehiculo_id: uuid.UUID
    puntaje: int
    created_at: datetime

    model_config = {"from_attributes": True}
