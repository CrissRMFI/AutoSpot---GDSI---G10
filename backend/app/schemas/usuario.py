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

class RegistroUsuarioSchema(BaseModel):
    """
    Payload de entrada para el registro de un nuevo Usuario.

    Campos:
        email    : Debe ser un correo electrónico con formato válido.
        password : Debe tener al menos 8 caracteres.

    Los demás datos del Usuario (nombre, apellido, etc.) se completan
    en una pantalla posterior (US 1U).
    """

    email: str
    password: str

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

class UsuarioPublicoSchema(BaseModel):
    """
    Respuesta pública del Usuario tras un registro exitoso.
    Nunca expone hashed_password ni datos sensibles.
    """

    id: uuid.UUID
    email: str
    is_active: bool

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

    Los campos heredados (id, email, is_active) mantienen compatibilidad
    con los tests existentes del login.
    """
    access_token: str
    token_type: str = "bearer"
