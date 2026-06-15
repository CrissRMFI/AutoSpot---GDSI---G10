from typing import Optional
from pydantic import BaseModel, Field

class DatosVehiculoIA(BaseModel):
    marca: str
    modelo: str
    anio: int
    tipo_transmision: str
    capacidad: int
    categoria: str
    tipo_combustible: str
    pets_friendly: bool
    
class SugerenciaPrecioIA(BaseModel):
    precio_minimo: float = Field(..., description="El valor más bajo recomendado por la IA")
    precio_recomendado: float = Field(..., description="El valor específicamente recomendado por la IA")
    precio_maximo: float = Field(..., description="El valor más alto recomendado por la IA")
    resumen: str = Field(..., description="Un breve resumen de los factores considerados para la estimación")
