"""
Schemas Pydantic — US 1C: Documentación habilitante del Conductor.

Responsabilidades:
    - Validar el payload de entrada de la documentación habilitante.
    - Representar la respuesta pública de la documentación registrada.

Criterios de Aceptación cubiertos:
    CA1 → número de licencia, categoría y fechas obligatorias.
    CA2 → foto frente y dorso de la licencia obligatorias.
    CA3 → campos vacíos, omitidos o fechas inconsistentes son rechazados.
"""
import uuid
from datetime import date

from pydantic import BaseModel, field_validator, model_validator

# Categorías de la Licencia Nacional de Conducir habilitadas para conducir autos.
CATEGORIAS_LICENCIA_VALIDAS = {"B1", "B2"}


class DocumentacionHabilitanteConductorSchema(BaseModel):
    """
    Payload de entrada para registrar o actualizar la documentación
    habilitante de un Conductor.

    Campos:
        categoria                  : Categoría/clase de la licencia.
        fecha_emision              : Fecha de emisión de la licencia.
        fecha_vencimiento          : Fecha de vencimiento de la licencia.
        foto_licencia_frente_url   : Ruta o URL de la foto del frente.
        foto_licencia_dorso_url    : Ruta o URL de la foto del dorso.
    """

    categoria: str
    fecha_emision: date
    fecha_vencimiento: date
    foto_licencia_frente_url: str
    foto_licencia_dorso_url: str

    @field_validator(
        "foto_licencia_frente_url",
        "foto_licencia_dorso_url",
    )
    @classmethod
    def validar_campo_obligatorio(cls, v: str) -> str:
        """CA3 — Rechaza campos obligatorios vacíos."""
        if not v or not v.strip():
            raise ValueError("Campo obligatorio")
        return v.strip()

    @field_validator("categoria")
    @classmethod
    def validar_categoria(cls, v: str) -> str:
        """CA3 — Solo se aceptan categorías de licencia conocidas."""
        if not v or not v.strip():
            raise ValueError("Campo obligatorio")

        categoria_normalizada = v.strip().upper()
        if categoria_normalizada not in CATEGORIAS_LICENCIA_VALIDAS:
            categorias_ordenadas = ", ".join(sorted(CATEGORIAS_LICENCIA_VALIDAS))
            raise ValueError(
                f"Categoria invalida. Valores permitidos: {categorias_ordenadas}"
            )
        return categoria_normalizada

    @model_validator(mode="after")
    def validar_fechas(self) -> "DocumentacionHabilitanteConductorSchema":
        """
        CA3 — La fecha de vencimiento debe ser posterior a la fecha de emisión.
        """
        if self.fecha_vencimiento <= self.fecha_emision:
            raise ValueError(
                "La fecha de vencimiento debe ser posterior a la fecha de emision"
            )
        return self


class DocumentacionHabilitanteConductorPublicoSchema(BaseModel):
    """
    Respuesta pública de la documentación habilitante registrada.

    Incluye estado de habilitación y motivo de rechazo (US 2C).
    """

    id: uuid.UUID
    usuario_id: uuid.UUID
    categoria: str
    fecha_emision: date
    fecha_vencimiento: date
    foto_licencia_frente_url: str
    foto_licencia_dorso_url: str
    estado_validacion: str
    motivo_rechazo: str | None = None

    model_config = {"from_attributes": True}
