"""
Controlador HTTP — US 8R: Checkout de Vehículo.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_admin
from app.exceptions import (
    CheckoutKilometrajeInvalidoError,
    CheckoutNoDisponibleError,
    CheckoutYaRegistradoError,
    ReservaNoEncontradaError,
)
from app.schemas.checkout_vehiculo import (
    CheckoutCreatePayloadSchema,
    CheckoutResponseSchema,
)
from app.services.checkout_service import crear_checkout, obtener_checkout_vigente


router = APIRouter(tags=["checkouts"])


@router.post(
    "/checkouts",
    response_model=CheckoutResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar checkout (inspección de devolución del vehículo)",
)
def crear_checkout_endpoint(
    payload: CheckoutCreatePayloadSchema,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(requerir_rol_admin),
):
    """
    US 8R — Permite al recepcionista registrar el estado del vehículo en la
    devolución. Solo disponible si el auto fue reportado como devuelto (US 7R).
    """
    try:
        return crear_checkout(
            db=db,
            schema=payload,
            recepcionista_id=uuid.UUID(str(usuario_actual["sub"])),
        )
    except ReservaNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CheckoutNoDisponibleError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except CheckoutKilometrajeInvalidoError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except CheckoutYaRegistradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/checkouts/reservas/{reserva_id}/vigente",
    response_model=CheckoutResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener checkout vigente de una reserva (admin)",
)
def obtener_checkout_vigente_admin_endpoint(
    reserva_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario_actual: dict = Depends(requerir_rol_admin),
):
    """
    Devuelve el último checkout de la reserva para la vista de recepción.
    """
    checkout = obtener_checkout_vigente(db=db, reserva_id=reserva_id)
    if checkout is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay checkout para esta reserva",
        )
    return checkout
