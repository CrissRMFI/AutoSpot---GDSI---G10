"""
Esquemas Pydantic para la gestión de alquileres.
"""
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.schemas.estacion import EstacionDetailResponse


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


class FotoVehiculoReservaSchema(BaseModel):
    """Foto del vehículo asociada al alquiler."""

    id: uuid.UUID
    lado: str
    url: str

    model_config = {"from_attributes": True}


class VehiculoReservaResumenSchema(BaseModel):
    """Datos del vehículo reservado/alquilado."""

    id: uuid.UUID
    marca: str
    modelo: str
    anio: int | None = None
    tipo_transmision: str | None = None
    capacidad: int | None = None
    categoria: str | None = None
    tipo_combustible: str | None = None
    pets_friendly: bool | None = None
    patente: str | None = None
    descripcion: str | None = None
    precio_por_dia: Decimal | None = None
    estacion: str
    fotos: list[FotoVehiculoReservaSchema] = Field(default_factory=list)


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
    fecha_entrega_solicitada: datetime | None = None
    fecha_salida_real: datetime | None = None
    fecha_devolucion_real: datetime | None = None
    monto_total: Decimal
    estacion_retiro: str
    motivo_rechazo: str | None = None
    minutos_retraso: int | None = None
    monto_penalizacion: Decimal | None = None
    vehiculo: VehiculoReservaResumenSchema
    estacion_detalle: EstacionDetailResponse | None = None

    model_config = {"from_attributes": True}


class VerificarCodigoReservaPayloadSchema(BaseModel):
    """Payload para verificar un código de reserva una sola vez."""

    codigo_reserva: str


class RechazarReservaPayloadSchema(BaseModel):
    """Payload para rechazar una reserva desde la verificación admin."""

    motivo: str = Field(..., min_length=1, max_length=500)


class ReservaVerificacionResponseSchema(ReservaCodigoResponseSchema):
    """Detalle admin de reserva"""

    conductor: ConductorReservaResumenSchema
    puede_entregar: bool
    motivo_bloqueo: str | None = None


class RegistrarEntradaResponseSchema(ReservaCodigoResponseSchema):
    """Respuesta de registrar la entrada/devolución del auto."""

    hubo_retraso: bool = False
    minutos_retraso: int | None = None
    monto_penalizacion: Decimal | None = None


class PaginaReservasSchema(BaseModel):
    """Página de reservas para listados paginados (Mis alquileres / Recepción)."""

    items: list[ReservaCodigoResponseSchema]
    total: int
    page: int
    size: int
    pages: int
