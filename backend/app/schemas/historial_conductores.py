"""
Esquemas Pydantic — US 11R: Historial de conductores.

Modelos de respuesta para el endpoint de historial de conductores
utilizado por el recepcionista (rol ADMIN).
"""
from decimal import Decimal
from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class AlquilerResumenSchema(BaseModel):
    """Resumen de un alquiler (reserva) asociado a un conductor."""

    id: uuid.UUID
    vehiculo_id: uuid.UUID
    estado: str
    fecha_inicio: datetime
    fecha_fin: datetime
    estacion_retiro: str
    monto_total: Decimal
    vehiculo_marca: str | None = None
    vehiculo_modelo: str | None = None
    vehiculo_patente: str | None = None
    created_at: datetime


class ConductorHistorialSchema(BaseModel):
    """Conductor con su lista de alquileres asociados."""

    id: uuid.UUID
    email: str
    nombre: str | None = None
    apellido: str | None = None
    dni: str | None = None
    alquileres: list[AlquilerResumenSchema] = Field(default_factory=list)
