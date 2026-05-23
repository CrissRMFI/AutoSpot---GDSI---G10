"""
Schemas Pydantic — Catálogo de Marcas y Modelos.

GET  /marcas                       → lista marcas con sus modelos anidados.
POST /marcas                       → crea una marca (ADMIN).
POST /marcas/{marca_id}/modelos    → crea un modelo bajo una marca (ADMIN).
"""
from pydantic import BaseModel, ConfigDict, field_validator


class MarcaCreateRequest(BaseModel):
    """Payload para crear una marca."""

    nombre: str

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        valor = (v or "").strip()
        if not valor:
            raise ValueError("Campo obligatorio")
        return valor


class ModeloCreateRequest(BaseModel):
    """Payload para crear un modelo bajo una marca."""

    nombre: str

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        valor = (v or "").strip()
        if not valor:
            raise ValueError("Campo obligatorio")
        return valor


class ModeloResponse(BaseModel):
    """Modelo serializado."""

    id: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)


class MarcaResponse(BaseModel):
    """Marca serializada con sus modelos anidados (formato esperado por el frontend)."""

    id: int
    nombre: str
    modelos: list[ModeloResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ModeloConMarcaResponse(BaseModel):
    """Modelo serializado incluyendo el id de su marca (respuesta del POST modelo)."""

    id: int
    marca_id: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)
