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


class AutoAlquileresDetalleSchema(BaseModel):
    """
    Detalle de un vehículo con sus alquileres (movimientos) para el panel admin.

    A diferencia de AutoHistorialSchema, devuelve siempre los datos del auto
    aunque no tenga movimientos, e incluye datos de presentación (año, estación,
    foto) para el encabezado de la vista.
    """

    id: uuid.UUID
    marca: str
    modelo: str
    anio: int | None = None
    patente: str | None = None
    estacion: str | None = None
    foto_url: str | None = None
    movimientos: list[MovimientoAutoSchema] = Field(default_factory=list)
