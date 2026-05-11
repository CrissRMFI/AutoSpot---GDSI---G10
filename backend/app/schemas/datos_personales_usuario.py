"""
Schemas Pydantic — US 1U: Registro datos personales.

Responsabilidades:
    - Validar el payload de entrada de datos personales.
    - Representar la respuesta pública de datos personales registrados.

Criterios de Aceptación cubiertos:
    CA1 → DNI, nombre y apellido obligatorios.
    CA2 → foto frente y dorso del DNI obligatorias.
    CA3 → si falta un campo obligatorio o es inválido, Pydantic debe rechazarlo.
"""
import uuid

from pydantic import BaseModel, field_validator


class DatosPersonalesUsuarioSchema(BaseModel):
    """
    Payload de entrada para registrar datos personales y documentación
    de un usuario que ya posee una cuenta creada.

    Campos:
        dni                  : Documento Nacional de Identidad.
        nombre               : Nombre del usuario.
        apellido             : Apellido del usuario.
        foto_dni_frente_url  : Ruta o URL de la foto del frente del DNI.
        foto_dni_dorso_url   : Ruta o URL de la foto del dorso del DNI.
    """

    dni: str
    nombre: str
    apellido: str
    foto_dni_frente_url: str
    foto_dni_dorso_url: str

    @field_validator(
        "dni",
        "nombre",
        "apellido",
        "foto_dni_frente_url",
        "foto_dni_dorso_url",
    )
    @classmethod
    def validar_campo_obligatorio(cls, v: str) -> str:
        """
        CA3 — Rechaza campos obligatorios vacíos o compuestos solo por espacios.

        Raises:
            ValueError: si el campo está vacío.
        """
        if not v or not v.strip():
            raise ValueError("Campo obligatorio")
        return v.strip()


class DatosPersonalesUsuarioPublicoSchema(BaseModel):
    """
    Respuesta pública de los datos personales registrados.
    """

    id: uuid.UUID
    usuario_id: uuid.UUID
    dni: str
    nombre: str
    apellido: str
    foto_dni_frente_url: str
    foto_dni_dorso_url: str
    estado_validacion: str

    model_config = {"from_attributes": True}
