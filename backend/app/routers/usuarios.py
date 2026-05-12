"""
Controlador HTTP: Usuarios.

Endpoints:
    POST /usuarios/registro  → CA 4 (registro exitoso) y CA 5 (mail existente)

Responsabilidades de esta capa:
    1. Recibir y deserializar el payload HTTP.
    2. Inyectar la sesión de DB vía dependency injection de FastAPI.
    3. Delegar la lógica de negocio al servicio `crear_usuario`.
    4. Traducir excepciones de dominio (MailExistenteError) a respuestas HTTP.
    5. Serializar la respuesta con UsuarioPublicoSchema (sin exponer datos sensibles).

Contrato HTTP (US 5U):
    - 201 Created     → registro exitoso, body = UsuarioPublicoSchema
    - 409 Conflict    → email ya registrado (CA 5)
    - 422 Unprocessable Entity → validación Pydantic fallida (CA 1 / CA 2),
                                 gestionado automáticamente por FastAPI.

Lenguaje Ubicuo (dominio_actores.md):
    - El prefijo de ruta es /usuarios (entidad base de autenticación).
    - Los actores Conductor/Propietario/Operador especializan esta entidad en USs futuras.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import MailExistenteError, CredencialesInvalidasError
from app.schemas.usuario import RegistroUsuarioSchema, UsuarioPublicoSchema, UsuarioLogin
from app.services.usuario import crear_usuario, autenticar_usuario

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
)


@router.post(
    "/registro",
    response_model=UsuarioPublicoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario con email y contraseña",
    description=(
        "Crea un nuevo Usuario base en la plataforma AutoSpot. "
        "La contraseña se hashea con bcrypt antes de persistirla. "
        "Nunca se almacena ni devuelve en texto plano."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Usuario registrado exitosamente.",
        },
        status.HTTP_409_CONFLICT: {
            "description": "El email ya está registrado en la plataforma.",
            "content": {
                "application/json": {
                    "example": {"detail": "Mail existente"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": (
                "Payload inválido: email con formato incorrecto "
                "o contraseña de menos de 8 caracteres."
            ),
        },
    },
)
def registrar_usuario(
    payload: RegistroUsuarioSchema,
    db: Session = Depends(get_db),
) -> UsuarioPublicoSchema:
    """
    POST /usuarios/registro

    Flujo:
        1. FastAPI deserializa el body y ejecuta los validadores de
           RegistroUsuarioSchema. Si fallan → 422 automático.
        2. Se llama a `crear_usuario` para verificar unicidad y persistir.
        3. Si el email ya existe → MailExistenteError → 409 Conflict.
        4. Si todo es correcto → se devuelve UsuarioPublicoSchema → 201 Created.

    Args:
        payload : Body JSON validado por RegistroUsuarioSchema.
        db      : Sesión de DB inyectada por FastAPI (get_db dependency).

    Returns:
        UsuarioPublicoSchema con `id`, `email` e `is_active`.
        Nunca incluye `hashed_password`.
    """
    try:
        usuario = crear_usuario(db=db, schema=payload)
    except MailExistenteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),  # → "Mail existente"
        ) from exc

    return UsuarioPublicoSchema.model_validate(usuario)

@router.post(
    "/login",
    response_model=UsuarioPublicoSchema,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión con email y contraseña",
    description="Autentica al usuario en el sistema usando su email y contraseña.",
    responses={
        status.HTTP_200_OK: {
            "description": "Usuario autenticado exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Credenciales inválidas (email o contraseña incorrectos).",
            "content": {
                "application/json": {
                    "example": {"detail": "Credenciales incorrectas"}
                }
            },
        },
    },
)
def iniciar_sesion(
    payload: UsuarioLogin,
    db: Session = Depends(get_db),
) -> UsuarioPublicoSchema:
    """
    POST /usuarios/login
    
    Verifica las credenciales del usuario y otorga acceso al sistema.
    Cumple con el criterio de seguridad de devolver un mensaje de error 
    genérico para proteger la existencia de la cuenta.
    """
    try:
        usuario = autenticar_usuario(db=db, credenciales=payload)
    except CredencialesInvalidasError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return UsuarioPublicoSchema.model_validate(usuario)
