"""
Utilidades de seguridad: hashing de contraseñas y gestión de tokens JWT.

Hashing:
  - Algoritmo: bcrypt (librería `bcrypt` directa, sin passlib).
  - `bcrypt.gensalt()` usa 12 rondas por defecto, suficiente para producción.

JWT (US 3U — Logout / Expiración):
  - Algoritmo: HS256 (HMAC-SHA256).
  - Cada token incluye `sub` (usuario), `exp` (expiración) y `jti` (ID único
    para invalidación vía blacklist).
  - SECRET_KEY se lee de la variable de entorno `JWT_SECRET_KEY` en producción.
    En desarrollo/test se usa un valor por defecto (NUNCA usar en producción).

Nota de compatibilidad:
  - passlib[bcrypt] tiene un bug conocido con bcrypt>=4.x (AttributeError en
    __about__.__version__). Se usa el módulo `bcrypt` directamente para evitarlo.
"""
import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# ── Configuración JWT ────────────────────────────────────────────────────────

SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "autospot-dev-secret-key-cambiar-en-produccion")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


def hash_password(plain_password: str) -> str:
    """
    Hashea una contraseña en texto plano usando bcrypt.

    Args:
        plain_password: Contraseña en texto plano (ya validada por el schema).

    Returns:
        String con el hash bcrypt, listo para persistir en `hashed_password`.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash bcrypt.

    Args:
        plain_password  : Contraseña ingresada por el usuario.
        hashed_password : Hash almacenado en la columna `hashed_password`.

    Returns:
        True si la contraseña es correcta, False en caso contrario.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ── JWT: Creación y verificación de tokens ───────────────────────────────────

def crear_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Genera un JSON Web Token (JWT) firmado con HS256.

    El token incluye:
      - `sub`: identificador del usuario (pasado en `data`).
      - `exp`: timestamp de expiración (CA2 — expiración por inactividad).
      - `jti`: UUID v4 único para invalidación vía blacklist (CA1 — logout).

    Args:
        data           : Diccionario con claims personalizados (mínimo `sub`).
        expires_delta  : Duración del token. Si es None, usa ACCESS_TOKEN_EXPIRE_MINUTES.
                         Puede ser negativo para tests de expiración.

    Returns:
        String codificado del JWT, listo para enviar al cliente.
    """
    to_encode = data.copy()

    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_access_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.

    Verifica:
      1. Firma válida (SECRET_KEY + ALGORITHM).
      2. Token no expirado (`exp` >= ahora).

    NO verifica blacklist; eso es responsabilidad de la capa de servicio.

    Args:
        token : String JWT recibido del header Authorization.

    Returns:
        Diccionario con los claims decodificados (sub, exp, jti, etc.).

    Raises:
        jwt.ExpiredSignatureError : Si el token ya expiró (CA2).
        jwt.InvalidTokenError     : Si la firma es inválida o el token está malformado.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
