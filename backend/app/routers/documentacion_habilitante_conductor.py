"""
Controlador HTTP — US 1C: Documentación habilitante del Conductor.

Endpoints:
    GET /usuarios/{usuario_id}/documentacion-habilitante
    PUT /usuarios/{usuario_id}/documentacion-habilitante
    PUT /usuarios/{usuario_id}/documentacion-habilitante/actualizar

Responsabilidades:
    1. Recibir y validar el payload HTTP con Pydantic.
    2. Exigir autenticación JWT.
    3. Verificar que el usuario autenticado opere solo sobre sus propios datos.
    4. Inyectar la sesión de DB.
    5. Delegar la lógica de negocio al servicio correspondiente.
    6. Traducir excepciones de dominio a respuestas HTTP.

Seguridad:
    - El claim `sub` del JWT debe coincidir con el `usuario_id` de la URL.
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
    DocumentacionHabilitanteNoRegistradaError,
    DocumentacionHabilitanteYaRegistradaError,
    UsuarioNoEncontradoError,
)
from app.schemas.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductorPublicoSchema,
    DocumentacionHabilitanteConductorSchema,
)
from app.services.documentacion_habilitante_conductor import (
    actualizar_documentacion_habilitante,
    obtener_documentacion_habilitante,
    registrar_documentacion_habilitante,
)


router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
)


@router.get(
    "/{usuario_id}/documentacion-habilitante",
    response_model=DocumentacionHabilitanteConductorPublicoSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener documentacion habilitante del Conductor",
    description=(
        "Retorna la documentación habilitante (licencia de conducir) del "
        "Conductor si ya fue registrada. Responde 404 si aún no la cargó."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Documentación habilitante obtenida."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Token ausente o inválido."},
        status.HTTP_403_FORBIDDEN: {"description": "Acceso a datos de otro usuario."},
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario no encontrado o documentación no registrada.",
        },
    },
)
def obtener_documentacion_habilitante_conductor(
    usuario_id: uuid.UUID,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> DocumentacionHabilitanteConductorPublicoSchema:
    """GET /usuarios/{usuario_id}/documentacion-habilitante"""
    validar_usuario_autenticado_coincide_con_id(
        usuario_id=usuario_id,
        usuario_actual=usuario_actual,
    )
    try:
        documentacion = obtener_documentacion_habilitante(
            db=db,
            usuario_id=usuario_id,
        )
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentacionHabilitanteNoRegistradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return DocumentacionHabilitanteConductorPublicoSchema.model_validate(documentacion)


@router.put(
    "/{usuario_id}/documentacion-habilitante",
    response_model=DocumentacionHabilitanteConductorPublicoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar documentacion habilitante del Conductor",
    description=(
        "Registra la licencia de conducir y sus fotos para el Conductor. "
        "Requiere autenticación JWT y solo permite operar sobre el usuario "
        "autenticado."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Documentación habilitante registrada exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario intenta operar sobre otro usuario.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario no encontrado.",
        },
        status.HTTP_409_CONFLICT: {
            "description": "El Conductor ya registró su documentación habilitante.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido o campos obligatorios faltantes.",
        },
    },
)
def registrar_documentacion_habilitante_conductor(
    usuario_id: uuid.UUID,
    payload: DocumentacionHabilitanteConductorSchema,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> DocumentacionHabilitanteConductorPublicoSchema:
    """PUT /usuarios/{usuario_id}/documentacion-habilitante"""
    validar_usuario_autenticado_coincide_con_id(
        usuario_id=usuario_id,
        usuario_actual=usuario_actual,
    )

    try:
        documentacion = registrar_documentacion_habilitante(
            db=db,
            usuario_id=usuario_id,
            schema=payload,
        )
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentacionHabilitanteYaRegistradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return DocumentacionHabilitanteConductorPublicoSchema.model_validate(documentacion)


@router.put(
    "/{usuario_id}/documentacion-habilitante/actualizar",
    response_model=DocumentacionHabilitanteConductorPublicoSchema,
    status_code=status.HTTP_200_OK,
    summary="Actualizar documentacion habilitante del Conductor",
    description=(
        "Actualiza la licencia de conducir y sus fotos para el Conductor. "
        "Requiere autenticación JWT y solo permite operar sobre el usuario "
        "autenticado."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Documentación habilitante actualizada exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario intenta operar sobre otro usuario.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario no encontrado o documentación no registrada.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido o campos obligatorios faltantes.",
        },
    },
)
def actualizar_documentacion_habilitante_conductor(
    usuario_id: uuid.UUID,
    payload: DocumentacionHabilitanteConductorSchema,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> DocumentacionHabilitanteConductorPublicoSchema:
    """PUT /usuarios/{usuario_id}/documentacion-habilitante/actualizar"""
    validar_usuario_autenticado_coincide_con_id(
        usuario_id=usuario_id,
        usuario_actual=usuario_actual,
    )

    try:
        documentacion = actualizar_documentacion_habilitante(
            db=db,
            usuario_id=usuario_id,
            schema=payload,
        )
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentacionHabilitanteNoRegistradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return DocumentacionHabilitanteConductorPublicoSchema.model_validate(documentacion)

@router.put(
    "/{usuario_id}/documentacion-habilitante/debug-toggle",
    status_code=status.HTTP_200_OK,
    summary="[DEBUG] Alternar estado de validación",
    description="Alterna el estado de validación de la documentación entre APROBADO y PENDIENTE_REVISION para facilitar pruebas locales.",
)
def debug_toggle_estado_documentacion(
    usuario_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    from app.models.documentacion_habilitante_conductor import DocumentacionHabilitanteConductor, EstadoHabilitacion
    doc = db.query(DocumentacionHabilitanteConductor).filter_by(usuario_id=usuario_id).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no tiene documentación cargada aún."
        )
        
    if doc.estado_validacion == EstadoHabilitacion.APROBADO:
        doc.estado_validacion = EstadoHabilitacion.PENDIENTE_REVISION
    else:
        doc.estado_validacion = EstadoHabilitacion.APROBADO
        
    db.commit()
    return {"mensaje": "Estado actualizado exitosamente", "nuevo_estado": doc.estado_validacion.value}
