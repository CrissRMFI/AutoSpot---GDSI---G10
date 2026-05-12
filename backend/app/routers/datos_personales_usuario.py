"""
Controlador HTTP — US 1U: Registro datos personales.

Endpoint temporal:
    PUT /usuarios/{usuario_id}/datos-personales

Nota técnica:
    Este endpoint recibe usuario_id explícito porque la US 2U de login/JWT
    todavía no está implementada. Cuando exista autenticación, este flujo
    debería migrar a /usuarios/me/datos-personales.

Responsabilidades:
    1. Recibir y validar el payload HTTP con Pydantic.
    2. Inyectar la sesión de DB.
    3. Delegar la lógica de negocio al servicio registrar_datos_personales.
    4. Traducir excepciones de dominio a respuestas HTTP.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import (
    DatosPersonalesYaRegistradosError,
    UsuarioNoEncontradoError,
)
from app.schemas.datos_personales_usuario import (
    DatosPersonalesUsuarioPublicoSchema,
    DatosPersonalesUsuarioSchema,
)
from app.services.datos_personales_usuario import registrar_datos_personales

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
)


@router.put(
    "/{usuario_id}/datos-personales",
    response_model=DatosPersonalesUsuarioPublicoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar datos personales del usuario",
    description=(
        "Registra DNI, nombre, apellido y documentación básica del usuario. "
        "Endpoint temporal hasta implementar autenticación/JWT."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Datos personales registrados exitosamente.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario no encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Usuario no encontrado"}
                }
            },
        },
        status.HTTP_409_CONFLICT: {
            "description": "El usuario ya registró sus datos personales.",
            "content": {
                "application/json": {
                    "example": {"detail": "Datos personales ya registrados"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Payload inválido o campos obligatorios faltantes.",
        },
    },
)
def registrar_datos_personales_usuario(
    usuario_id: uuid.UUID,
    payload: DatosPersonalesUsuarioSchema,
    db: Session = Depends(get_db),
) -> DatosPersonalesUsuarioPublicoSchema:
    """
    PUT /usuarios/{usuario_id}/datos-personales

    Flujo:
        1. FastAPI valida usuario_id como UUID y el body con Pydantic.
        2. El servicio verifica que el Usuario exista.
        3. El servicio verifica que no existan datos personales previos.
        4. Si todo es correcto, persiste y retorna los datos registrados.

    Returns:
        DatosPersonalesUsuarioPublicoSchema.
    """
    try:
        datos_personales = registrar_datos_personales(
            db=db,
            usuario_id=usuario_id,
            schema=payload,
        )
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DatosPersonalesYaRegistradosError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return DatosPersonalesUsuarioPublicoSchema.model_validate(datos_personales)
