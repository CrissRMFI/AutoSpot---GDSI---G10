"""
Controlador HTTP — US 1D: Cargar características y fotos del auto.

Endpoint temporal:
    POST /usuarios/{propietario_id}/vehiculos

Nota técnica:
    Este endpoint recibe propietario_id explícito porque todavía no existe
    autenticación/JWT ni especialización formal del rol Propietario.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import UsuarioNoEncontradoError
from app.schemas.vehiculo import (
    RegistroVehiculoPayloadSchema,
    RegistroVehiculoSchema,
    VehiculoPublicoSchema,
)
from app.services.vehiculo import registrar_vehiculo

router = APIRouter(
    prefix="/usuarios",
    tags=["vehiculos"],
)


@router.post(
    "/{propietario_id}/vehiculos",
    response_model=VehiculoPublicoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar vehículo con características y fotos",
    description=(
        "Registra características obligatorias y fotos del vehículo. "
        "Endpoint temporal hasta implementar autenticación/JWT y rol Propietario."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Vehículo registrado exitosamente.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Propietario no encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Usuario no encontrado"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Payload inválido.",
        },
    },
)
def registrar_vehiculo_usuario(
    propietario_id: uuid.UUID,
    payload: RegistroVehiculoPayloadSchema,
    db: Session = Depends(get_db),
) -> VehiculoPublicoSchema:
    """
    POST /usuarios/{propietario_id}/vehiculos

    Flujo:
        1. FastAPI valida propietario_id como UUID.
        2. FastAPI/Pydantic valida el payload.
        3. Se construye el schema de servicio incorporando propietario_id.
        4. El servicio verifica que el propietario exista y persiste el vehículo.
    """
    schema = RegistroVehiculoSchema(
        propietario_id=propietario_id,
        **payload.model_dump(),
    )

    try:
        vehiculo = registrar_vehiculo(db=db, schema=schema)
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return VehiculoPublicoSchema.model_validate(vehiculo)
