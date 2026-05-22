"""
Controlador HTTP — US 1R y 2R: Solicitudes de documentación pendientes.

Endpoint:
    GET /admin/solicitudes-documentacion

Responsabilidades:
    1. Exigir autenticación JWT.
    2. Restringir el acceso a usuarios con rol ADMIN (recepcionista).
    3. Delegar la consulta al servicio de dominio.
    4. Serializar la respuesta con el schema público.

Seguridad:
    - 401: token ausente o inválido.
    - 403: usuario autenticado sin rol ADMIN.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_admin
from app.schemas.solicitud_documentacion import SolicitudDocumentacionSchema
from app.services.solicitud_documentacion import listar_solicitudes_pendientes


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get(
    "/solicitudes-documentacion",
    response_model=list[SolicitudDocumentacionSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar solicitudes de documentación pendientes",
    description=(
        "Devuelve la cola de solicitudes de documentación pendientes de "
        "validación (vehículos en EN_REVISION y conductores en "
        "PENDIENTE_VALIDACION), ordenada cronológicamente de la más antigua "
        "a la más reciente. Si no hay trámites pendientes, retorna lista "
        "vacía. Reservado al rol ADMIN."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Cola de solicitudes obtenida exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado no tiene rol ADMIN.",
        },
    },
)
def listar_solicitudes_documentacion(
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> list[SolicitudDocumentacionSchema]:
    """GET /admin/solicitudes-documentacion"""
    return listar_solicitudes_pendientes(db=db)
