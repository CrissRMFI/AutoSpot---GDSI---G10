"""
Controlador HTTP — US 15C: Check-in de Vehículo.
"""
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_usuario_actual
from app.schemas.checkin_vehiculo import (
    CheckinCreatePayloadSchema,
    CheckinResponseSchema,
    CheckinUpdatePayloadSchema,
)
from app.services.checkin_service import crear_checkin, re_enviar_checkin


router = APIRouter(tags=["checkins"])


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
        conductor_id=uuid.UUID(usuario_actual["sub"]),
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
        conductor_id=uuid.UUID(usuario_actual["sub"]),
    )


@router.get(
    "/admin/checkins/pendientes",
    response_model=list[CheckinResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar check-ins pendientes",
)
def listar_checkins_pendientes_endpoint(
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(get_usuario_actual),
):
    from fastapi import HTTPException
    from app.services.checkin_service import listar_checkins_pendientes
    if usuario_actual.get("rol") != "ADMIN":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    return listar_checkins_pendientes(db)


@router.post(
    "/admin/checkins/{checkin_id}/aprobar",
    response_model=CheckinResponseSchema,
    status_code=status.HTTP_200_OK,
)
def aprobar_checkin_endpoint(
    checkin_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(get_usuario_actual),
):
    from fastapi import HTTPException
    from app.services.checkin_service import aprobar_checkin
    if usuario_actual.get("rol") != "ADMIN":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    return aprobar_checkin(db, checkin_id)


from pydantic import BaseModel
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
    usuario_actual: dict = Depends(get_usuario_actual),
):
    from fastapi import HTTPException
    from app.services.checkin_service import rechazar_checkin
    if usuario_actual.get("rol") != "ADMIN":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    return rechazar_checkin(db, checkin_id, payload.motivo)
