"""
Dependencies de autenticación para rutas protegidas.

Responsabilidades:
    1. Extraer el token Bearer del header Authorization.
    2. Validar firma, expiración y blacklist del JWT.
    3. Exponer el payload del usuario autenticado a los routers.
    4. Rechazar requests sin token o con token inválido.

Uso esperado en routers:

    usuario_actual = Depends(get_usuario_actual)

El payload esperado del token incluye:
    - sub: UUID del usuario autenticado
    - exp: fecha de expiración
    - jti: identificador único del token
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import TokenInvalidoError
from app.models.usuario import Usuario
from app.services.usuario import validar_token_activo


security_scheme = HTTPBearer(auto_error=False)


def get_token_bearer(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> str:
    """
    Extrae el token Bearer del header Authorization.

    Args:
        credentials: Credenciales HTTP Bearer provistas por FastAPI.

    Returns:
        Token JWT como string.

    Raises:
        HTTPException 401: Si no se envió token.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    return credentials.credentials


def get_usuario_actual(
    token: str = Depends(get_token_bearer),
    db: Session = Depends(get_db),
) -> dict:
    """
    Valida el token JWT y retorna el payload del usuario autenticado.

    Verifica:
        1. Firma válida.
        2. Token no expirado.
        3. Token no invalidado por logout.
        4. Presencia del claim `sub`.

    Args:
        token: JWT extraído del header Authorization.
        db: Sesión de base de datos.

    Returns:
        Payload decodificado del JWT.

    Raises:
        HTTPException 401: Si el token es inválido o no contiene `sub`.
    """
    try:
        payload = validar_token_activo(db=db, token=token)
    except TokenInvalidoError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    return payload


def validar_usuario_autenticado_coincide_con_id(
    usuario_id,
    usuario_actual: dict,
) -> None:
    """
    Verifica que el usuario autenticado opere sobre su propio recurso.

    Ejemplo:
        Si el token tiene sub = 123, no puede modificar /usuarios/456.

    Args:
        usuario_id: UUID recibido por path parameter.
        usuario_actual: Payload del JWT validado.

    Raises:
        HTTPException 403: Si el usuario intenta operar sobre otro usuario.
    """
    if str(usuario_id) != str(usuario_actual.get("sub")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede operar sobre otro usuario",
        )


def requerir_rol_admin(
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> dict:
    """
    Verifica que el usuario autenticado tenga rol ADMIN.

    Pensado para rutas operativas reservadas al recepcionista/administrador
    (por ejemplo, la cola de solicitudes de documentación de las US 1R y 2R).

    Raises:
        HTTPException 401: Si no se pudo identificar al usuario (sub inválido).
        HTTPException 403: Si el usuario no tiene rol ADMIN.
    """
    usuario_id = usuario_actual.get("sub")
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if usuario is None or (usuario.rol or "").upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación reservada al rol ADMIN",
        )

    return usuario_actual


def requerir_rol_cliente(
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> dict:
    """
    Verifica que el usuario autenticado tenga rol CLIENTE.

    Se usa para acciones propias del conductor, como confirmar una reserva
    desde el catálogo.
    """
    usuario_id = usuario_actual.get("sub")
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if usuario is None or (usuario.rol or "").upper() != "CLIENTE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación reservada al rol CLIENTE",
        )

    return usuario_actual
