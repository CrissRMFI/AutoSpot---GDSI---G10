"""
Schemas Pydantic — US 1R y 2R: Solicitudes de documentación pendientes.

Responsabilidades:
    - Representar la respuesta pública de una solicitud pendiente de revisión.
    - Unificar solicitudes de vehículos (US 2D) y conductores (US 1C) en una
      cola única para la pantalla del recepcionista.

Criterios de Aceptación cubiertos:
    US 1R CA1 → retorna el conjunto de datos de los usuarios con documentación
                en revisión.
    US 1R CA2 → confirma lista vacía cuando no hay trámites pendientes.
    US 2R CA1 → orden cronológico ascendente (más antiguos primero).
    US 2R CA2 → los nuevos ingresos quedan al final de la secuencia.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel


TIPO_SOLICITUD_VEHICULO = "VEHICULO"
TIPO_SOLICITUD_CONDUCTOR = "CONDUCTOR"


class SolicitudDocumentacionSchema(BaseModel):
    """
    Solicitud de documentación pendiente de revisión por un recepcionista/admin.

    Campos:
        tipo            : "VEHICULO" o "CONDUCTOR".
        recurso_id      : UUID del recurso (vehículo o documentación habilitante).
        usuario_id      : UUID del usuario al que pertenece la solicitud.
        usuario_email   : Email del usuario, útil para identificarlo en la cola.
        estado          : Estado actual del trámite.
        fecha_solicitud : Timestamp UTC de la última actualización del registro,
                          usado para ordenar la cola cronológicamente.
        resumen         : Descripción corta para mostrar en la lista.
    """

    tipo: str
    recurso_id: uuid.UUID
    usuario_id: uuid.UUID
    usuario_email: str
    estado: str
    fecha_solicitud: datetime
    resumen: str

    model_config = {"from_attributes": True}
