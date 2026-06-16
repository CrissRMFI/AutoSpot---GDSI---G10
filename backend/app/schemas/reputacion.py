"""
Esquemas Pydantic — US 17D: Métricas de reputación y satisfacción.
"""
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class ReseniaDetalleSchema(BaseModel):
    """Detalle de una reseña individual histórica."""

    puntaje: int
    conductor: str
    comentario: Optional[str] = None
    fecha: datetime

    model_config = {"from_attributes": True}


class MetricasReputacionSchema(BaseModel):
    """Métricas agregadas y detalle de reseñas de un vehículo."""

    promedio_estrellas: float
    cantidad_total: int
    resenias: List[ReseniaDetalleSchema]

    model_config = {"from_attributes": True}
