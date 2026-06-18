"""
Esquemas Pydantic — US 16C / Reportes criticos de incidencia durante el alquiler.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

FORMATOS_FOTO_PERMITIDOS = {"jpg", "jpeg", "png", "webp"}
MIN_FOTOS_REPORTE = 1
MAX_FOTOS_REPORTE = 10


class ReporteFotoPayloadSchema(BaseModel):
    """Foto adjunta enviada por el conductor al crear el reporte."""

    url: str = Field(..., max_length=500, description="URL pública de la foto en Cloudinary.")
    descripcion: str = Field(
        ...,
        max_length=500,
        description="Descripción obligatoria de la foto.",
    )
    formato: str = Field(..., max_length=20, description="Formato del archivo.")
    tamanio_bytes: int = Field(..., gt=0, description="Tamaño del archivo en bytes (> 0).")
    orden: int = Field(..., ge=1, description="Orden de la foto dentro del reporte (>= 1).")

    @field_validator("url", "descripcion", "formato")
    @classmethod
    def _no_vacio(cls, valor: str) -> str:
        limpio = (valor or "").strip()
        if not limpio:
            raise ValueError("El campo no puede estar vacío.")
        return limpio

    @field_validator("formato")
    @classmethod
    def _formato_permitido(cls, valor: str) -> str:
        formato = valor.lower()
        if formato not in FORMATOS_FOTO_PERMITIDOS:
            permitidos = ", ".join(sorted(FORMATOS_FOTO_PERMITIDOS))
            raise ValueError(f"Formato '{formato}' no permitido. Usá: {permitidos}.")
        return formato


class ReportePayloadSchema(BaseModel):
    """Payload HTTP para registrar un reporte de falla critica.

    `reserva_id` se recibe como path parameter en el endpoint, por lo que no
    es requerido en el body. Los campos tipo/criticidad/estado los fija el
    backend; el cliente solo envía descripción y fotos.
    """

    descripcion: str = Field(
        ...,
        max_length=1000,
        description="Texto libre del conductor describiendo el problema.",
    )
    fotos: list[ReporteFotoPayloadSchema] = Field(
        ...,
        description="Entre 1 y 10 fotos, cada una con descripción obligatoria.",
    )

    @field_validator("descripcion")
    @classmethod
    def _descripcion_no_vacia(cls, valor: str) -> str:
        limpio = (valor or "").strip()
        if not limpio:
            raise ValueError("La descripción es obligatoria.")
        return limpio

    @field_validator("fotos")
    @classmethod
    def _cantidad_fotos(
        cls, fotos: list[ReporteFotoPayloadSchema]
    ) -> list[ReporteFotoPayloadSchema]:
        if len(fotos) < MIN_FOTOS_REPORTE:
            raise ValueError("Se requiere al menos una foto.")
        if len(fotos) > MAX_FOTOS_REPORTE:
            raise ValueError(f"No se permiten más de {MAX_FOTOS_REPORTE} fotos.")
        return fotos


class ResolverReportePayloadSchema(BaseModel):
    """Payload para registrar la resolución de un reporte."""

    resolucion_descripcion: str = Field(
        ...,
        max_length=1000,
        description="Descripción obligatoria de la resolución.",
    )

    @field_validator("resolucion_descripcion")
    @classmethod
    def _resolucion_no_vacia(cls, valor: str) -> str:
        limpio = (valor or "").strip()
        if not limpio:
            raise ValueError("La descripción de la resolución es obligatoria.")
        return limpio


class ReporteFotoResponseSchema(BaseModel):
    """Respuesta pública de una foto de reporte."""

    id: uuid.UUID
    url: str
    descripcion: str
    formato: str
    tamanio_bytes: int
    orden: int

    model_config = {"from_attributes": True}


class ReporteResponseSchema(BaseModel):
    """Respuesta pública de un reporte registrado."""

    id: uuid.UUID
    reserva_id: uuid.UUID
    conductor_id: uuid.UUID
    vehiculo_id: uuid.UUID
    descripcion: str
    tipo: str
    criticidad: str
    estado: str
    resuelto_at: datetime | None
    resuelto_por_id: uuid.UUID | None
    resolucion_descripcion: str | None
    created_at: datetime
    fotos: list[ReporteFotoResponseSchema] = []

    model_config = {"from_attributes": True}


class ReporteDetalleSchema(ReporteResponseSchema):
    """Detalle del reporte enriquecido con datos del vehículo y la reserva."""

    codigo_reserva: str | None = None
    vehiculo_marca: str | None = None
    vehiculo_modelo: str | None = None
    vehiculo_anio: int | None = None

    model_config = {"from_attributes": True}
