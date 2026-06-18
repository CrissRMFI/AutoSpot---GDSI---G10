"""
Esquemas Pydantic — US 10R: Historial de autos.

Modelos de respuesta para el endpoint de historial de autos
utilizado por el recepcionista (rol ADMIN).
"""
from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class MovimientoAutoSchema(BaseModel):
    """Movimiento individual (reserva) de un vehículo."""

    id: uuid.UUID
    conductor_id: uuid.UUID
    conductor_email: str
    conductor_nombre: str | None = None
    conductor_apellido: str | None = None
    estado: str
    fecha_inicio: datetime
    fecha_fin: datetime
    estacion_retiro: str
    created_at: datetime


class AutoHistorialSchema(BaseModel):
    """Vehículo con su lista de movimientos (reservas)."""

    id: uuid.UUID
    marca: str
    modelo: str
    patente: str | None = None
    movimientos: list[MovimientoAutoSchema] = Field(default_factory=list)
