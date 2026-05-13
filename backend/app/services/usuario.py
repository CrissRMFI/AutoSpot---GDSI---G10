"""
Servicio de negocio: Usuario.

Responsabilidades de esta capa:
    1. Verificar unicidad del email antes de persistir (CA 5 — US 5U).
    2. Delegar el hashing al módulo de seguridad (CA 4 — US 5U).
    3. Persistir el nuevo Usuario y retornarlo hidratado con su id.
    4. Autenticar usuario con email y contraseña (US 2U).
    5. Cerrar sesión invalidando el token JWT vía blacklist (CA1 — US 3U).
    6. Validar tokens activos verificando firma, expiración y blacklist (US 3U).

Esta capa NO valida formato de email ni longitud de contraseña;
esa responsabilidad pertenece al schema Pydantic (RegistroUsuarioSchema).
"""

import uuid
from datetime import datetime, timezone

import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import (
    MailExistenteError,
    MailInexistenteError,
    ContraseniaIncorrectaError,
    UsuarioNoEncontradoError,
    TokenInvalidoError,
)
from app.models.token_blacklist import TokenBlacklist
from app.models.usuario import Usuario
from app.schemas.usuario import RegistroUsuarioSchema, UsuarioLogin
from app.utils.security import hash_password, verify_password, verificar_access_token


def crear_usuario(db: Session, schema: RegistroUsuarioSchema) -> Usuario:
    """
    Crea un nuevo Usuario en la base de datos.

    Flujo:
        1. Consulta si el email ya existe → lanza MailExistenteError (CA 5).
        2. Hashea la contraseña con bcrypt (CA 4 - nunca texto plano).
        3. Instancia y persiste el Usuario.
        4. En caso de race condition, el IntegrityError de DB también se
           convierte en MailExistenteError.

    Args:
        db     : Sesión SQLAlchemy activa (inyectada por el controlador o el test).
        schema : Payload ya validado por RegistroUsuarioSchema
                 (email normalizado a minúsculas, contraseña ≥ 8 chars).

    Returns:
        El objeto Usuario persistido, con `id` y `created_at` poblados.

    Raises:
        MailExistenteError: Si el email ya está registrado en la plataforma.
    """
    email_existente = (
        db.query(Usuario)
        .filter(Usuario.email == schema.email)
        .first()
    )

    if email_existente:
        raise MailExistenteError()

    nuevo_usuario = Usuario(
        email=schema.email,
        hashed_password=hash_password(schema.password),
    )

    db.add(nuevo_usuario)

    try:
        db.commit()
        db.refresh(nuevo_usuario)
    except IntegrityError:
        db.rollback()
        raise MailExistenteError()

    return nuevo_usuario


def actualizar_usuario(
    db: Session,
    usuario_id: uuid.UUID,
    schema: RegistroUsuarioSchema,
) -> Usuario:
    """
    Actualiza los datos de un Usuario existente.

    Flujo:
        1. Verifica que el Usuario exista.
        2. Verifica unicidad del nuevo email, si se está actualizando.
        3. Hashea la nueva contraseña, si se está actualizando.
        4. Actualiza los campos y persiste los cambios.

    Args:
        db         : Sesión SQLAlchemy activa.
        usuario_id : UUID del Usuario a actualizar.
        schema     : Payload con los campos a actualizar.

    Returns:
        El objeto Usuario actualizado.

    Raises:
        UsuarioNoEncontradoError: Si no existe un Usuario con ese id.
        MailExistenteError: Si el nuevo email ya pertenece a otro Usuario.
    """
    usuario = (
        db.query(Usuario)
        .filter(Usuario.id == usuario_id)
        .first()
    )

    if not usuario:
        raise UsuarioNoEncontradoError()

    if schema.email and schema.email != usuario.email:
        email_existente = (
            db.query(Usuario)
            .filter(
                Usuario.email == schema.email,
                Usuario.id != usuario_id,
            )
            .first()
        )

        if email_existente:
            raise MailExistenteError()

        usuario.email = schema.email

    if schema.password:
        usuario.hashed_password = hash_password(schema.password)

    db.commit()
    db.refresh(usuario)

    return usuario


def autenticar_usuario(db: Session, credenciales: UsuarioLogin) -> Usuario:
    """
    Autentica un usuario verificando su email y contraseña.

    Args:
        db: Sesión de la base de datos.
        credenciales: Schema con email y contraseña.

    Returns:
        El modelo de Usuario si las credenciales son válidas.

    Raises:
        MailInexistenteError: Si el email no existe.
        ContraseniaIncorrectaError: Si la contraseña no coincide.
    """
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == credenciales.email)
        .first()
    )

    if not usuario:
        raise MailInexistenteError()

    if not verify_password(credenciales.password, usuario.hashed_password):
        raise ContraseniaIncorrectaError()

    return usuario


def cerrar_sesion(db: Session, token: str) -> None:
    """
    Invalida un token JWT insertando su `jti` en la blacklist.

    Flujo (CA1 — Logout manual):
        1. Decodifica el token para extraer `jti` y `exp`.
        2. Verifica que el `jti` no esté ya en la blacklist.
        3. Inserta el `jti` en la tabla `tokens_blacklist`.

    Args:
        db    : Sesión SQLAlchemy activa.
        token : String JWT del header Authorization.

    Raises:
        TokenInvalidoError : Si el token es inválido, expirado o ya fue
                             invalidado previamente.
    """
    try:
        payload = verificar_access_token(token)
    except jwt.ExpiredSignatureError:
        raise TokenInvalidoError("Token expirado")
    except jwt.InvalidTokenError:
        raise TokenInvalidoError("Token inválido")

    jti = payload.get("jti")

    if not jti:
        raise TokenInvalidoError("Token inválido")

    ya_invalidado = (
        db.query(TokenBlacklist)
        .filter(TokenBlacklist.jti == jti)
        .first()
    )

    if ya_invalidado:
        raise TokenInvalidoError("Token inválido")

    registro = TokenBlacklist(
        jti=jti,
        expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
    )

    db.add(registro)
    db.commit()


def validar_token_activo(db: Session, token: str) -> dict:
    """
    Valida que un token JWT sea válido Y no esté en la blacklist.

    Flujo:
        1. Decodifica el token (verifica firma + expiración).
        2. Consulta la blacklist por `jti`.
        3. Si todo es correcto, retorna el payload decodificado.

    Args:
        db    : Sesión SQLAlchemy activa.
        token : String JWT del header Authorization.

    Returns:
        Diccionario con los claims del token (sub, exp, jti, etc.).

    Raises:
        TokenInvalidoError : Si el token es inválido, expirado o blacklisteado.
    """
    try:
        payload = verificar_access_token(token)
    except jwt.ExpiredSignatureError:
        raise TokenInvalidoError("Token expirado")
    except jwt.InvalidTokenError:
        raise TokenInvalidoError("Token inválido")

    jti = payload.get("jti")

    if not jti:
        raise TokenInvalidoError("Token inválido")

    en_blacklist = (
        db.query(TokenBlacklist)
        .filter(TokenBlacklist.jti == jti)
        .first()
    )

    if en_blacklist:
        raise TokenInvalidoError("Token inválido")

    return payload