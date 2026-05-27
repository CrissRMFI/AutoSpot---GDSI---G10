"""
Controlador HTTP — US 1R y 2R: Solicitudes de documentación pendientes.

Endpoints:
    GET /admin/solicitudes-documentacion
    GET /admin/solicitudes-documentacion/{tipo}/{recurso_id}

Responsabilidades:
    1. Exigir autenticación JWT.
    2. Restringir el acceso a usuarios con rol ADMIN (recepcionista).
    3. Delegar la consulta al servicio de dominio.
    4. Serializar la respuesta con el schema público.

Seguridad:
    - 401: token ausente o inválido.
    - 403: usuario autenticado sin rol ADMIN.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_admin
from app.exceptions import (
    SolicitudDocumentacionNoEncontradaError,
    TipoSolicitudDocumentacionInvalidoError,
)
from app.schemas.solicitud_documentacion import (
    ResolucionRechazoSchema,
    SolicitudDocumentacionDetalleSchema,
    SolicitudDocumentacionSchema,
)
from app.services.solicitud_documentacion import (
    listar_solicitudes_pendientes,
    obtener_detalle_solicitud_documentacion,
    resolver_solicitud,
)


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
        "PENDIENTE_REVISION), ordenada cronológicamente de la más antigua "
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


@router.get(
    "/solicitudes-documentacion/{tipo}/{recurso_id}",
    response_model=SolicitudDocumentacionDetalleSchema,
    status_code=status.HTTP_200_OK,
    summary="Abrir documentacion de una solicitud",
    description=(
        "Devuelve el detalle completo de una solicitud de documentacion "
        "para que el ADMIN pueda revisar datos e imagenes antes de validar."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Detalle de documentacion obtenido."},
        status.HTTP_400_BAD_REQUEST: {"description": "Tipo de solicitud invalido."},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, invalido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado no tiene rol ADMIN.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Solicitud de documentacion no encontrada.",
        },
    },
)
def abrir_solicitud_documentacion(
    tipo: str,
    recurso_id: uuid.UUID,
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> SolicitudDocumentacionDetalleSchema:
    """GET /admin/solicitudes-documentacion/{tipo}/{recurso_id}"""
    try:
        return obtener_detalle_solicitud_documentacion(
            db=db,
            tipo=tipo,
            recurso_id=recurso_id,
        )
    except TipoSolicitudDocumentacionInvalidoError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except SolicitudDocumentacionNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/solicitudes-documentacion/{tipo}/{recurso_id}/aprobar",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Aprobar documentación",
    description="Aprueba la solicitud de documentación habilitando al conductor o al vehículo.",
)
def aprobar_solicitud(
    tipo: str,
    recurso_id: uuid.UUID,
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
):
    """POST /admin/solicitudes-documentacion/{tipo}/{recurso_id}/aprobar"""
    try:
        resolver_solicitud(db, tipo, recurso_id, aprobada=True)
    except TipoSolicitudDocumentacionInvalidoError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SolicitudDocumentacionNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/solicitudes-documentacion/{tipo}/{recurso_id}/rechazar",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Rechazar documentación",
    description="Rechaza la solicitud de documentación indicando un motivo.",
)
def rechazar_solicitud(
    tipo: str,
    recurso_id: uuid.UUID,
    payload: ResolucionRechazoSchema,
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
):
    """POST /admin/solicitudes-documentacion/{tipo}/{recurso_id}/rechazar"""
    try:
        resolver_solicitud(db, tipo, recurso_id, aprobada=False, motivo_rechazo=payload.motivo_rechazo)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except TipoSolicitudDocumentacionInvalidoError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SolicitudDocumentacionNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
