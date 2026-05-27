"""
Esquemas Pydantic para la gestión de alquileres.
"""
from pydantic import BaseModel, Field
from datetime import datetime


class SimularTiempoAlquilerRequest(BaseModel):
    """Payload para solicitar la simulación y validación de tiempo."""
    fecha_inicio: datetime = Field(..., description="Fecha y hora de inicio del alquiler")
    fecha_fin: datetime = Field(..., description="Fecha y hora de fin del alquiler")


class SimularTiempoAlquilerResponse(BaseModel):
    """Respuesta con el cálculo exacto de tiempo."""
    dias: int = Field(..., description="Cantidad de días completos de alquiler")
    horas: int = Field(..., description="Cantidad de horas adicionales de alquiler")
