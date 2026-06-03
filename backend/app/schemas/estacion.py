from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EstacionBase(BaseModel):
    nombre: str
    direccion: str
    zona: str
    activa: bool
    imagen_url: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


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


class EstacionCreateRequest(BaseModel):
    """
    Payload para crear una nueva estación a mano (admin).
    """
    nombre: str = Field(..., description="Nombre de la nueva estación (Ej: Spot Centro)")
    descripcion: str = Field(..., description="Descripción o instrucciones de acceso para el conductor")
    latitud: float = Field(..., description="Coordenada de latitud (Ej: -34.6037)")
    longitud: float = Field(..., description="Coordenada de longitud (Ej: -58.3816)")
