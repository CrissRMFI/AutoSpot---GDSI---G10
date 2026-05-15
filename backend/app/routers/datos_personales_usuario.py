"""
Controlador HTTP — US 1U y US 4U: Datos personales del usuario.

Endpoints:
    PUT /usuarios/{usuario_id}/datos-personales
    PUT /usuarios/{usuario_id}/datos-personales/actualizar

Responsabilidades:
    1. Recibir y validar el payload HTTP con Pydantic.
    2. Exigir autenticación JWT.
    3. Verificar que el usuario autenticado opere solo sobre sus propios datos.
    4. Inyectar la sesión de DB.
    5. Delegar la lógica de negocio al servicio correspondiente.
    6. Traducir excepciones de dominio a respuestas HTTP.

Seguridad:
    - El claim `sub` del JWT debe coincidir con el `usuario_id` de la URL.
    - Un usuario no puede registrar ni modificar datos personales de otro usuario.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    get_usuario_actual,
    validar_usuario_autenticado_coincide_con_id,
)
from app.exceptions import (
    DatosPersonalesYaRegistradosError,
    DatosPersonalesNoRegistradosError,
    UsuarioNoEncontradoError,
    DniYaRegistradoError,
)
from app.schemas.datos_personales_usuario import (
    DatosPersonalesUsuarioPublicoSchema,
    DatosPersonalesUsuarioSchema,
)
from app.services.datos_personales_usuario import (
    registrar_datos_personales,
    actualizar_datos_personales,
)


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
        "Requiere autenticación JWT y solo permite operar sobre el usuario "
        "autenticado."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Datos personales registrados exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta operar sobre otro usuario.",
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
            "description": "El usuario ya registró sus datos personales o el DNI ya existe.",
            "content": {
                "application/json": {
                    "examples": {
                        "datos_duplicados": {
                            "value": {"detail": "Datos personales ya registrados"}
                        },
                        "dni_duplicado": {
                            "value": {"detail": "DNI ya registrado"}
                        },
                    }
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido o campos obligatorios faltantes.",
        },
    },
)
def registrar_datos_personales_usuario(
    usuario_id: uuid.UUID,
    payload: DatosPersonalesUsuarioSchema,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> DatosPersonalesUsuarioPublicoSchema:
    """
    PUT /usuarios/{usuario_id}/datos-personales

    Flujo:
        1. FastAPI valida usuario_id como UUID y el body con Pydantic.
        2. Se valida el JWT.
        3. Se verifica que el `sub` del JWT coincida con `usuario_id`.
        4. El servicio verifica que el Usuario exista.
        5. El servicio verifica que no existan datos personales previos.
        6. Si todo es correcto, persiste y retorna los datos registrados.

    Returns:
        DatosPersonalesUsuarioPublicoSchema.
    """
    validar_usuario_autenticado_coincide_con_id(
        usuario_id=usuario_id,
        usuario_actual=usuario_actual,
    )

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
    except DniYaRegistradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return DatosPersonalesUsuarioPublicoSchema.model_validate(datos_personales)


@router.put(
    "/{usuario_id}/datos-personales/actualizar",
    response_model=DatosPersonalesUsuarioPublicoSchema,
    status_code=status.HTTP_200_OK,
    summary="Actualizar datos personales del usuario",
    description=(
        "Actualiza DNI, nombre, apellido y documentación básica del usuario. "
        "Requiere autenticación JWT y solo permite operar sobre el usuario "
        "autenticado."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Datos personales actualizados exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta operar sobre otro usuario.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario no encontrado o datos personales no registrados.",
            "content": {
                "application/json": {
                    "example": {"detail": "Usuario no encontrado"}
                }
            },
        },
        status.HTTP_409_CONFLICT: {
            "description": "El DNI ya está registrado por otro usuario.",
            "content": {
                "application/json": {
                    "example": {"detail": "DNI ya registrado"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido o campos obligatorios faltantes.",
        },
    },
)
def actualizar_datos_personales_usuario(
    usuario_id: uuid.UUID,
    payload: DatosPersonalesUsuarioSchema,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> DatosPersonalesUsuarioPublicoSchema:
    """
    PUT /usuarios/{usuario_id}/datos-personales/actualizar

    Flujo:
        1. FastAPI valida usuario_id como UUID y el body con Pydantic.
        2. Se valida el JWT.
        3. Se verifica que el `sub` del JWT coincida con `usuario_id`.
        4. El servicio verifica que el Usuario exista.
        5. El servicio verifica que existan datos personales previos para actualizar.
        6. Si todo es correcto, actualiza, persiste y retorna los datos.

    Returns:
        DatosPersonalesUsuarioPublicoSchema.
    """
    validar_usuario_autenticado_coincide_con_id(
        usuario_id=usuario_id,
        usuario_actual=usuario_actual,
    )

    try:
        datos_personales = actualizar_datos_personales(
            db=db,
            usuario_id=usuario_id,
            schema=payload,
        )
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DatosPersonalesNoRegistradosError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DniYaRegistradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return DatosPersonalesUsuarioPublicoSchema.model_validate(datos_personales)