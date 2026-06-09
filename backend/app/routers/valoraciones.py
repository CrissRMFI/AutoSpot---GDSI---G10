"""
Controlador HTTP — US 17C: Valoración cuantitativa del servicio.

Endpoint:
    POST /valoraciones — Registra una valoración (puntaje 1–5) para una
    reserva finalizada con devolución. Requiere rol CLIENTE.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_cliente
from app.exceptions import (
    ReservaNoEncontradaError,
    ReservaNoFinalizadaError,
    ValoracionYaRegistradaError,
)
from app.schemas.valoracion import (
    ValoracionCreatePayloadSchema,
    ValoracionResponseSchema,
)
from app.services.valoracion_service import crear_valoracion


router = APIRouter(tags=["Valoraciones"])


@router.post(
    "/valoraciones",
    response_model=ValoracionResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar valoración cuantitativa del servicio (US 17C)",
)
def crear_valoracion_endpoint(
    payload: ValoracionCreatePayloadSchema,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(requerir_rol_cliente),
) -> ValoracionResponseSchema:
    """
    US 17C — El conductor asigna un puntaje de 1 a 5 a una contratación
    finalizada con devolución física registrada.

    Al registrar la valoración, el sistema recalcula automáticamente el
    promedio del vehículo y del propietario.
    """
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))

    try:
        valoracion = crear_valoracion(
            db=db,
            reserva_id=payload.reserva_id,
            conductor_id=conductor_id,
            puntaje=payload.puntaje,
        )
    except ReservaNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ReservaNoFinalizadaError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ValoracionYaRegistradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return valoracion
