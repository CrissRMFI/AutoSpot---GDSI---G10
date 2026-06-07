"""
Esquemas Pydantic — US 18C: Testimonio descriptivo de la experiencia.

Define los contratos de entrada y salida para el endpoint de testimonios.

Reglas de negocio reflejadas:
  - El campo `descripcion` es OPCIONAL (puede omitirse o enviarse vacío).
  - Un testimonio se vincula de forma permanente a una reserva (1 a 1).
  - Una vez creado, el testimonio es inmutable (no hay endpoint de edición).
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TestimonioCreatePayloadSchema(BaseModel):
    """
    Payload HTTP para registrar un testimonio descriptivo.

    El campo `descripcion` es opcional: el conductor puede enviar el formulario
    sin escribir nada. La vinculación al viaje y al vehículo se realiza a través
    del `reserva_id` de la reserva finalizada.
    """

    reserva_id: uuid.UUID = Field(
        ...,
        description="ID de la reserva finalizada sobre la cual se deja el testimonio.",
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=1000,
        description=(
            "Texto libre con la experiencia del conductor (máx. 2000 caracteres). "
            "Campo opcional: puede omitirse o enviarse vacío."
        ),
    )


class TestimonioResponseSchema(BaseModel):
    """
    Respuesta pública de un testimonio registrado.

    Expone los campos necesarios para integrar el relato al historial de
    confianza del vehículo consultable por futuros conductores (CA 2).
    """

    id: uuid.UUID
    reserva_id: uuid.UUID
    conductor_id: uuid.UUID
    vehiculo_id: uuid.UUID
    descripcion: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
