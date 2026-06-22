from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict


class IncidenteAutoSchema(BaseModel):
    marca: str
    modelo: str
    patente: str | None


class IncidenteUsuarioSchema(BaseModel):
    nombre: str
    apellido: str


class IncidenteListResponseSchema(BaseModel):
    id: uuid.UUID
    codigo_reserva: str
    fecha: datetime
    estado: str
    auto: IncidenteAutoSchema
    conductor: IncidenteUsuarioSchema

    model_config = ConfigDict(from_attributes=True)


class IncidenteDetalleResponseSchema(IncidenteListResponseSchema):
    descripcion: str
    propietario: IncidenteUsuarioSchema
    fotos: list[str]

    model_config = ConfigDict(from_attributes=True)
