from pydantic import BaseModel, ConfigDict


class EstacionBase(BaseModel):
    nombre: str
    direccion: str
    zona: str
    activa: bool


class EstacionListResponse(EstacionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EstacionDetailResponse(EstacionBase):
    id: int
    instrucciones_acceso: str

    model_config = ConfigDict(from_attributes=True)
