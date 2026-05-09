"""
Utilidades de seguridad: hashing y verificación de contraseñas.

Algoritmo: bcrypt (librería `bcrypt` directa, sin passlib).

Nota de compatibilidad:
  - passlib[bcrypt] tiene un bug conocido con bcrypt>=4.x (AttributeError en
    __about__.__version__). Se usa el módulo `bcrypt` directamente para evitarlo.
  - `bcrypt.gensalt()` usa 12 rondas por defecto, suficiente para producción.
"""
import bcrypt


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

