"""
Schemas Pydantic para la entidad Usuario.

Esta capa es responsable de la validación del payload de entrada (CA 1 y CA 2
de la US 5U). Los mensajes de error son los canónicos definidos en los
Criterios de Aceptación.

Referencia de CAs cubiertos aquí:
  CA 1 → email inválido     → "Mail invalido"
  CA 2 → contraseña corta   → "La contrasenia debe tener minimo 8 caracteres"
"""
import re
import uuid
from pydantic import BaseModel, field_validator

# Expresión regular RFC 5322 simplificada, suficiente para validación
# de formato básico de email (evita dependencia de email-validator en tests).
_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

# Roles que un usuario puede elegir en el registro público.
# ADMIN queda excluido y se crea exclusivamente por backoffice.
ROLES_REGISTRO_PUBLICO = {"CLIENTE", "PROPIETARIO"}
ROLES_VALIDOS = ROLES_REGISTRO_PUBLICO | {"ADMIN"}


class RegistroUsuarioSchema(BaseModel):
    """
    Payload de entrada para el registro de un nuevo Usuario.

    Campos:
        email    : Debe ser un correo electrónico con formato válido.
        password : Debe tener al menos 8 caracteres.
        rol      : CLIENTE o PROPIETARIO. ADMIN no se permite en el registro
                   público y se rechaza con 422.
    """

    email: str
    password: str
    rol: str = "CLIENTE"

    @field_validator("email")
    @classmethod
    def validar_email(cls, v: str) -> str:
        """
        CA 1 — Valida formato de email.
        Normaliza a minúsculas antes de retornar.

        Raises:
            ValueError: con mensaje "Mail invalido" si el formato no es válido.
        """
        if not v or not _EMAIL_REGEX.match(v.strip()):
            raise ValueError("Mail invalido")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validar_contrasenia(cls, v: str) -> str:
        """
        CA 2 — Valida longitud mínima de contraseña.

        Raises:
            ValueError: con mensaje exacto del CA 2 si tiene < 8 caracteres.
        """
        if len(v) < 8:
            raise ValueError("La contraseña debe tener minimo 8 caracteres")
        return v

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, v: str) -> str:
        """
        Normaliza el rol y bloquea el alta de ADMIN desde el registro público.
        ADMIN solo se crea por backoffice (Postman/seed).
        """
        valor = (v or "").strip().upper()
        if valor not in ROLES_REGISTRO_PUBLICO:
            raise ValueError("Rol invalido")
        return valor


class UsuarioPublicoSchema(BaseModel):
    """
    Respuesta pública del Usuario tras un registro exitoso.
    Nunca expone hashed_password ni datos sensibles.
    """

    id: uuid.UUID
    email: str
    is_active: bool
    rol: str

    model_config = {"from_attributes": True}

class UsuarioLogin(BaseModel):
    """
    Payload de entrada para el inicio de sesión.
    No requiere validaciones estrictas de longitud como el registro,
    sino solo formato base para procesar contra la base de datos.
    """
    email: str
    password: str


class LoginResponseSchema(UsuarioPublicoSchema):
    """
    Respuesta del login exitoso (US 2U + US 3U).

    Extiende UsuarioPublicoSchema con los campos de autenticación JWT:
      - access_token : Token JWT firmado para autenticar requests posteriores.
      - token_type   : Siempre "bearer" (estándar OAuth2).
    """
    access_token: str
    token_type: str = "bearer"
