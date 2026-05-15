"""
Controlador HTTP: Usuarios.

Endpoints:
    POST /usuarios/registro  → CA 4 (registro exitoso) y CA 5 (mail existente)
    POST /usuarios/login     → Autenticación con email y contraseña (US 2U)
    POST /usuarios/logout    → Finalización de sesión (US 3U)

Responsabilidades de esta capa:
    1. Recibir y deserializar el payload HTTP.
    2. Inyectar la sesión de DB vía dependency injection de FastAPI.
    3. Delegar la lógica de negocio a los servicios correspondientes.
    4. Traducir excepciones de dominio a respuestas HTTP.
    5. Serializar la respuesta con los schemas apropiados.

Contrato HTTP:
    US 5U (Registro):
        - 201 Created     → registro exitoso, body = UsuarioPublicoSchema
        - 409 Conflict    → email ya registrado (CA 5)
        - 422 Unprocessable Entity → validación Pydantic fallida (CA 1 / CA 2)
    US 2U (Login):
        - 200 OK           → login exitoso, body = LoginResponseSchema (con access_token)
        - 401 Unauthorized → credenciales inválidas
    US 3U (Logout):
        - 200 OK           → sesión finalizada correctamente
        - 401 Unauthorized → token ausente, inválido, expirado o ya invalidado

Lenguaje Ubicuo (dominio_actores.md):
    - El prefijo de ruta es /usuarios (entidad base de autenticación).
    - Los actores Conductor/Propietario/Operador especializan esta entidad en USs futuras.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    get_usuario_actual,
    validar_usuario_autenticado_coincide_con_id,
)
from app.exceptions import (
    MailExistenteError,
    MailInexistenteError,
    ContraseniaIncorrectaError,
    UsuarioNoEncontradoError,
    TokenInvalidoError,
)
from app.exceptions import (
    MailExistenteError,
    MailInexistenteError,
    ContraseniaIncorrectaError,
    UsuarioNoEncontradoError,
    TokenInvalidoError,
)
from app.schemas.usuario import (
    RegistroUsuarioSchema,
    UsuarioPublicoSchema,
    UsuarioLogin,
    LoginResponseSchema,
)
from app.services.usuario import (
    crear_usuario,
    autenticar_usuario,
    cerrar_sesion,
    actualizar_usuario as actualizar_usuario_service,
)
from app.utils.security import crear_access_token

# ── Esquema de seguridad para Bearer token ───────────────────────────────────
# auto_error=False para manejar la ausencia de token manualmente (→ 401, no 403)
security_scheme = HTTPBearer(auto_error=False)

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

@router.put(
    "/{usuario_id}/actualizar",
    response_model=UsuarioPublicoSchema,
    status_code=status.HTTP_200_OK,
    summary="Actualizar datos de un usuario existente",
    description=(
        "Permite actualizar la información de un Usuario existente. "
        "El email debe ser único y la contraseña se hashea antes de persistir. "
        "Requiere autenticación JWT y solo permite que el usuario autenticado "
        "actualice su propia cuenta."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Usuario actualizado exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta operar sobre otro usuario.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario no encontrado.",
        },
        status.HTTP_409_CONFLICT: {
            "description": "El email ya está registrado en la plataforma.",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": (
                "Payload inválido: email con formato incorrecto "
                "o contraseña de menos de 8 caracteres."
            ),
        },
    },
)


def actualizar_usuario(
    usuario_id: uuid.UUID,
    payload: RegistroUsuarioSchema,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> UsuarioPublicoSchema:
    """
    Actualiza los datos de un Usuario existente.

    Seguridad:
        - Requiere JWT válido.
        - El `sub` del token debe coincidir con el `usuario_id` de la URL.
        - Un usuario no puede actualizar la cuenta de otro usuario.

    Flujo:
        1. FastAPI valida el payload.
        2. Se valida el token JWT mediante get_usuario_actual.
        3. Se compara usuario_id del path contra sub del token.
        4. Se delega la actualización al servicio de dominio.
        5. Se traducen errores de dominio a HTTP.
    """
    validar_usuario_autenticado_coincide_con_id(
        usuario_id=usuario_id,
        usuario_actual=usuario_actual,
    )

    try:
        usuario = actualizar_usuario_service(
            db=db,
            usuario_id=usuario_id,
            schema=payload,
        )
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except MailExistenteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return UsuarioPublicoSchema.model_validate(usuario)

@router.post(
    "/login",
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión con email y contraseña",
    description=(
        "Autentica al usuario en el sistema usando su email y contraseña. "
        "Devuelve un access_token JWT para autenticar requests posteriores."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Usuario autenticado exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Credenciales inválidas (email inexistente o contraseña incorrecta).",
            "content": {
                "application/json": {
                    "examples": {
                        "mail_inexistente": {"value": {"detail": "Email inexistente"}},
                        "contrasenia_incorrecta": {"value": {"detail": "Contraseña incorrecta"}}
                    }
                }
            },
        },
    },
)
def iniciar_sesion(
    payload: UsuarioLogin,
    db: Session = Depends(get_db),
) -> LoginResponseSchema:
    """
    POST /usuarios/login

    Flujo:
        1. Verifica credenciales delegando a `autenticar_usuario`.
        2. Si son válidas, genera un JWT con `sub` = usuario.id.
        3. Retorna LoginResponseSchema con access_token + datos públicos.

    El token incluye `jti` (para logout/blacklist) y `exp` (expiración
    automática por inactividad — CA2 de US 3U).
    """
    try:
        usuario = autenticar_usuario(db=db, credenciales=payload)
    except MailInexistenteError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except ContraseniaIncorrectaError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    # ── Generar JWT (US 3U) ──────────────────────────────────────────────
    access_token = crear_access_token(data={"sub": str(usuario.id)})

    return LoginResponseSchema(
        id=usuario.id,
        email=usuario.email,
        is_active=usuario.is_active,
        access_token=access_token,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Finalizar sesión del usuario (US 3U)",
    description=(
        "Invalida el token JWT del usuario insertando su identificador "
        "único (jti) en la blacklist. El token no podrá reutilizarse."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Sesión finalizada correctamente.",
            "content": {
                "application/json": {
                    "example": {"detail": "Sesión finalizada correctamente"}
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o ya invalidado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Token inválido"}
                }
            },
        },
    },
)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """
    POST /usuarios/logout

    Flujo (CA1 — Logout manual):
        1. Extrae el Bearer token del header Authorization.
        2. Si no hay token → 401.
        3. Delega a `cerrar_sesion` para validar e insertar en blacklist.
        4. Si el token es inválido/expirado/ya invalidado → 401.
        5. Si todo es correcto → 200 con mensaje de confirmación.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    try:
        cerrar_sesion(db=db, token=credentials.credentials)
    except TokenInvalidoError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return {"detail": "Sesión finalizada correctamente"}
