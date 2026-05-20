from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EstacionBase(BaseModel):
    nombre: str
    direccion: str
    zona: str
    activa: bool
    imagen_url: Optional[str] = None


class EstacionListResponse(EstacionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EstacionDetailResponse(EstacionBase):
    id: int
    instrucciones_acceso: str

    model_config = ConfigDict(from_attributes=True)


class EstacionImagenUpdateRequest(BaseModel):
    """
    Payload para PATCH /estaciones/{id}/imagen.

    Se usa principalmente desde Postman para asignar la URL de la imagen de la estación.
    """

    imagen_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL pública de la imagen de la estación. Enviar null para limpiar.",
    )
