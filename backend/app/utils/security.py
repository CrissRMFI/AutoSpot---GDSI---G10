"""
Utilidades de seguridad: hashing de contraseñas y gestión de tokens JWT.

Hashing:
  - Algoritmo: bcrypt, usando la librería `bcrypt` directamente.
  - `bcrypt.gensalt()` usa 12 rondas por defecto.

JWT:
  - El algoritmo se lee desde `JWT_ALGORITHM`.
  - La clave secreta se lee desde `JWT_SECRET_KEY`.
  - La expiración se lee desde `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`.
  - Cada token incluye `sub`, `exp` y `jti`.
  - `jti` permite invalidar tokens mediante blacklist.

Nota:
  - No se define una SECRET_KEY por defecto. Si falta la variable de entorno,
    el backend debe fallar temprano en vez de arrancar con una clave insegura.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# ── Configuración JWT ────────────────────────────────────────────────────────

SECRET_KEY: str | None = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY no está configurada")

ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)


# ── Hashing de contraseñas ───────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Hashea una contraseña en texto plano usando bcrypt.

    Args:
        plain_password: Contraseña en texto plano, previamente validada.

    Returns:
        String con el hash bcrypt listo para persistir.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash bcrypt.

    Args:
        plain_password: Contraseña ingresada por el usuario.
        hashed_password: Hash almacenado en la base de datos.

    Returns:
        True si la contraseña es correcta, False en caso contrario.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ── JWT: creación y verificación de tokens ───────────────────────────────────

def crear_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Genera un JSON Web Token firmado.

    El token incluye:
      - sub: identificador del usuario.
      - exp: fecha/hora de expiración.
      - jti: UUID único del token, usado para blacklist.

    Args:
        data: Claims personalizados. Debe incluir al menos `sub`.
        expires_delta: Duración personalizada del token. Si es None,
            usa JWT_ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        JWT codificado como string.
    """
    to_encode = data.copy()

    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verificar_access_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.

    Verifica:
      1. Firma válida.
      2. Algoritmo permitido.
      3. Token no expirado.

    No verifica blacklist; eso corresponde a la capa de servicio.

    Args:
        token: JWT recibido desde el header Authorization.

    Returns:
        Claims decodificados del token.

    Raises:
        jwt.ExpiredSignatureError: Si el token expiró.
        jwt.InvalidTokenError: Si el token es inválido.
    """
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )