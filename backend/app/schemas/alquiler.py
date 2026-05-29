"""
Esquemas Pydantic para la gestión de alquileres.
"""
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class SimularTiempoAlquilerRequest(BaseModel):
    """Payload para solicitar la simulación y validación de tiempo."""
    fecha_inicio: datetime = Field(..., description="Fecha y hora de inicio del alquiler")
    fecha_fin: datetime = Field(..., description="Fecha y hora de fin del alquiler")


class SimularTiempoAlquilerResponse(BaseModel):
    """Respuesta con el cálculo exacto de tiempo."""
    dias: int = Field(..., description="Cantidad de días completos de alquiler")
    horas: int = Field(..., description="Cantidad de horas adicionales de alquiler")


class CrearReservaPayloadSchema(BaseModel):
    """Payload HTTP para confirmar una reserva y obtener el código."""

    vehiculo_id: uuid.UUID
    fecha_inicio: datetime
    fecha_fin: datetime


class VehiculoReservaResumenSchema(BaseModel):
    """Datos pactados del vehículo reservado que acompañan el código."""

    id: uuid.UUID
    marca: str
    modelo: str
    patente: str | None = None
    estacion: str


class ConductorReservaResumenSchema(BaseModel):
    """Datos del conductor requeridos por US 5R para verificar identidad."""

    id: uuid.UUID
    email: str
    nombre: str | None = None
    apellido: str | None = None
    dni: str | None = None


class ReservaCodigoResponseSchema(BaseModel):
    """Respuesta pública de US 14C con código de reserva."""

    id: uuid.UUID
    vehiculo_id: uuid.UUID
    conductor_id: uuid.UUID
    estado: str
    codigo_reserva: str
    codigo_verificado_at: datetime | None = None
    fecha_inicio: datetime
    fecha_fin: datetime
    monto_total: Decimal
    estacion_retiro: str
    motivo_rechazo: str | None = None
    vehiculo: VehiculoReservaResumenSchema

    model_config = {"from_attributes": True}


class VerificarCodigoReservaPayloadSchema(BaseModel):
    """Payload para verificar un código de reserva una sola vez."""

    codigo_reserva: str


class RechazarReservaPayloadSchema(BaseModel):
    """Payload para rechazar una reserva desde la verificación admin."""

    motivo: str = Field(..., min_length=1, max_length=500)


class ReservaVerificacionResponseSchema(ReservaCodigoResponseSchema):
    """Detalle admin de reserva para US 5R."""

    conductor: ConductorReservaResumenSchema
    puede_entregar: bool
    motivo_bloqueo: str | None = None
