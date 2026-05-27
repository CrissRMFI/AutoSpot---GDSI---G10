"""
Controlador HTTP — Notificaciones del usuario autenticado.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_usuario_actual
from app.exceptions import NotificacionNoEncontradaError
from app.schemas.notificacion import NotificacionSchema
from app.services.notificacion import (
    listar_notificaciones_no_vistas,
    marcar_notificacion_como_vista,
)


router = APIRouter(
    prefix="/notificaciones",
    tags=["notificaciones"],
)


def _usuario_id_desde_token(usuario_actual: dict) -> uuid.UUID:
    return uuid.UUID(str(usuario_actual["sub"]))


@router.get(
    "",
    response_model=list[NotificacionSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar notificaciones nuevas",
    description=(
        "Devuelve las notificaciones no vistas del usuario autenticado. "
        "Cuando una notificación se marca como vista deja de aparecer."
    ),
)
def listar_notificaciones(
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> list[NotificacionSchema]:
    """GET /notificaciones"""
    return listar_notificaciones_no_vistas(
        db=db,
        usuario_id=_usuario_id_desde_token(usuario_actual),
    )


@router.post(
    "/{notificacion_id}/vista",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marcar notificación como vista",
    description="Marca una notificación propia como vista para ocultarla de la campana.",
)
def marcar_notificacion_vista(
    notificacion_id: uuid.UUID,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> None:
    """POST /notificaciones/{notificacion_id}/vista"""
    try:
        marcar_notificacion_como_vista(
            db=db,
            usuario_id=_usuario_id_desde_token(usuario_actual),
            notificacion_id=notificacion_id,
        )
    except NotificacionNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
