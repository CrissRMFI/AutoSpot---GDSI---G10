"""
Esquemas Pydantic — US 15C: Check-in de Vehículo.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CheckinBaseSchema(BaseModel):
    nivel_combustible: str = Field(
        ...,
        description="Nivel de combustible: 1/4, 1/2, 3/4, Lleno",
    )
    kilometraje_actual: int = Field(
        ...,
        ge=0,
        description=(
            "Kilometraje (odómetro) del vehículo. En el check-in se autocompleta "
            "desde el vehículo en el backend (no lo carga el conductor)."
        ),
    )
    esta_limpio: bool = Field(
        ...,
        description="Indicador de si el vehículo está limpio.",
    )
    tiene_danios: bool = Field(
        ...,
        description="Indicador de si el vehículo presenta rayas o daños.",
    )
    descripcion_danios: str | None = Field(
        None,
        max_length=500,
        description="Descripción obligatoria si tiene_danios es True.",
    )
    
    url_foto_frente: str = Field(..., description="Foto frente.")
    url_foto_trasera: str = Field(..., description="Foto trasera.")
    url_foto_lateral_izq: str = Field(..., description="Foto lateral izquierdo.")
    url_foto_lateral_der: str = Field(..., description="Foto lateral derecho.")
    url_foto_panel: str = Field(..., description="Foto del panel (km/combustible).")

    urls_fotos_danios: list[str] = Field(
        default_factory=list,
        max_length=5,
        description="Fotos de daños (máximo 5).",
    )
    url_foto_extra: str | None = Field(
        None,
        description="Foto extra opcional.",
    )
    notas_adicionales: str | None = Field(
        None,
        max_length=500,
        description="Comentarios adicionales opcionales.",
    )

    @field_validator("descripcion_danios")
    @classmethod
    def validar_descripcion_danios(cls, v: str | None, info) -> str | None:
        """Si tiene_danios es True, la descripción no puede ser nula ni vacía."""
        tiene_danios = info.data.get("tiene_danios")
        if tiene_danios is True and not v:
            raise ValueError("Debe proveer una descripción si indica que hay daños.")
        return v

    @field_validator("urls_fotos_danios")
    @classmethod
    def validar_fotos_danios(cls, v: list[str], info) -> list[str]:
        """Si tiene_danios es True, debe proveer al menos 1 foto."""
        tiene_danios = info.data.get("tiene_danios")
        if tiene_danios is True and not v:
            raise ValueError("Debe proveer al menos una foto del daño reportado.")
        return v


class CheckinCreatePayloadSchema(CheckinBaseSchema):
    reserva_id: uuid.UUID


class CheckinUpdatePayloadSchema(CheckinBaseSchema):
    """
    Schema para re-enviar un check-in rechazado.
    No requiere enviar reserva_id ya que se actualiza la misma entidad.
    """
    pass


class CheckinResponseSchema(CheckinBaseSchema):
    id: uuid.UUID
    reserva_id: uuid.UUID
    conductor_id: uuid.UUID
    estado: str
    motivo_rechazo: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehiculoResumenCheckinSchema(BaseModel):
    """Datos mínimos del vehículo para la vista admin de check-ins."""

    marca: str | None = None
    modelo: str | None = None
    patente: str | None = None


class ReservaResumenCheckinSchema(BaseModel):
    """
    Resumen de la reserva asociada a un check-in, para la lista admin.

    Permite mostrar el código real (AS-XXXXXX), el conductor y la patente
    en lugar del UUID, y habilita el filtrado en el frontend.
    """

    codigo: str | None = None
    conductor_nombre: str | None = None
    estacion_retiro: str | None = None
    fecha_inicio: datetime | None = None
    vehiculo: VehiculoResumenCheckinSchema | None = None


class CheckinAdminItemSchema(CheckinResponseSchema):
    """Check-in enriquecido con el resumen de su reserva (vista admin)."""

    reserva: ReservaResumenCheckinSchema | None = None
