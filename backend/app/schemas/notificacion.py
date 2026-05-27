"""
Schemas Pydantic — Notificaciones de usuario.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel


class NotificacionSchema(BaseModel):
    """
    Notificación no vista por el usuario autenticado.
    """

    id: uuid.UUID
    usuario_id: uuid.UUID
    tipo: str
    titulo: str
    mensaje: str
    recurso_tipo: str | None = None
    recurso_id: uuid.UUID | None = None
    created_at: datetime
    vista_at: datetime | None = None

    model_config = {"from_attributes": True}
