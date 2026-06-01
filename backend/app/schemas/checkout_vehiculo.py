"""
Esquemas Pydantic — US 8R: Checkout de Vehículo.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CheckoutBaseSchema(BaseModel):
    nivel_combustible: str = Field(
        ...,
        description="Nivel de combustible: 1/4, 1/2, 3/4, Lleno",
    )
    kilometraje_actual: int = Field(
        ...,
        gt=0,
        description="Kilometraje marcado en el panel al devolver el auto.",
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


class CheckoutCreatePayloadSchema(CheckoutBaseSchema):
    reserva_id: uuid.UUID


class CheckoutResponseSchema(CheckoutBaseSchema):
    id: uuid.UUID
    reserva_id: uuid.UUID
    recepcionista_id: uuid.UUID
    estado: str
    motivo_rechazo: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RechazarCheckoutPayloadSchema(BaseModel):
    motivo: str = Field(..., min_length=1, max_length=500)
