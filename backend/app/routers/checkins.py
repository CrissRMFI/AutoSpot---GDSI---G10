"""
Controlador HTTP — US 15C: Check-in de Vehículo.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_usuario_actual, requerir_rol_admin
from app.schemas.checkin_vehiculo import (
    CheckinCreatePayloadSchema,
    CheckinResponseSchema,
    CheckinUpdatePayloadSchema,
)
from app.services.checkin_service import (
    aprobar_checkin,
    crear_checkin,
    listar_checkins,
    listar_checkins_pendientes,
    obtener_checkin,
    re_enviar_checkin,
    rechazar_checkin,
)


router = APIRouter(tags=["checkins"])


def _obtener_usuario_id(usuario_actual: dict) -> uuid.UUID:
    usuario_id = usuario_actual.get("sub") or usuario_actual.get("id")
    return uuid.UUID(str(usuario_id))


@router.post(
    "/checkins",
    response_model=CheckinResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar check-in inicial del vehículo",
)
def crear_checkin_endpoint(
    payload: CheckinCreatePayloadSchema,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(get_usuario_actual),
):
    """
    Permite al conductor registrar el estado inicial de un vehículo.
    """
    return crear_checkin(
        db=db,
        schema=payload,
        conductor_id=_obtener_usuario_id(usuario_actual),
    )


@router.put(
    "/checkins/{checkin_id}",
    response_model=CheckinResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un check-in rechazado",
)
def re_enviar_checkin_endpoint(
    checkin_id: uuid.UUID,
    payload: CheckinUpdatePayloadSchema,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(get_usuario_actual),
):
    """
    Permite reenviar el formulario si fue rechazado por el administrador.
    """
    return re_enviar_checkin(
        db=db,
        checkin_id=checkin_id,
        schema=payload,
        conductor_id=_obtener_usuario_id(usuario_actual),
    )


@router.get(
    "/admin/checkins",
    response_model=list[CheckinResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los check-ins",
)
def listar_checkins_endpoint(
    db: Session = Depends(get_db),
    _usuario_actual: dict = Depends(requerir_rol_admin),
):
    return listar_checkins(db)


@router.get(
    "/admin/checkins/pendientes",
    response_model=list[CheckinResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar check-ins pendientes",
)
def listar_checkins_pendientes_endpoint(
    db: Session = Depends(get_db),
    _usuario_actual: dict = Depends(requerir_rol_admin),
):
    return listar_checkins_pendientes(db)


@router.get(
    "/admin/checkins/{checkin_id}",
    response_model=CheckinResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener un check-in por id",
)
def obtener_checkin_endpoint(
    checkin_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario_actual: dict = Depends(requerir_rol_admin),
):
    checkin = obtener_checkin(db, checkin_id)
    if checkin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in no encontrado")
    return checkin


@router.post(
    "/admin/checkins/{checkin_id}/aprobar",
    response_model=CheckinResponseSchema,
    status_code=status.HTTP_200_OK,
)
def aprobar_checkin_endpoint(
    checkin_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario_actual: dict = Depends(requerir_rol_admin),
):
    return aprobar_checkin(db, checkin_id)


class RechazarPayload(BaseModel):
    motivo: str


@router.post(
    "/admin/checkins/{checkin_id}/rechazar",
    response_model=CheckinResponseSchema,
    status_code=status.HTTP_200_OK,
)
def rechazar_checkin_endpoint(
    checkin_id: uuid.UUID,
    payload: RechazarPayload,
    db: Session = Depends(get_db),
    _usuario_actual: dict = Depends(requerir_rol_admin),
):
    return rechazar_checkin(db, checkin_id, payload.motivo)
