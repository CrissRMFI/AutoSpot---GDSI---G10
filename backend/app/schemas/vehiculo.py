"""
Schemas Pydantic — US 1D: Cargar características y fotos del auto.

Responsabilidades:
    - Validar el payload de entrada para registrar un vehículo.
    - Validar los datos básicos de las fotos asociadas.
    - Preparar la respuesta pública del vehículo registrado.

Criterios de Aceptación cubiertos progresivamente:
    CA1 → campos obligatorios.
    CA2 → año válido.
    CA3 → formato y tamaño de foto.
    CA5 → cantidad mínima de fotos requeridas.
    CA6 → registro exitoso con campos correctos.
"""
from decimal import Decimal
import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator


ANIO_MINIMO_PERMITIDO = 1990
TAMANIO_MAXIMO_FOTO_BYTES = 5 * 1024 * 1024

FORMATOS_FOTO_PERMITIDOS = {"jpg", "jpeg", "png", "webp"}

LADOS_FOTO_REQUERIDOS = {
    "FRENTE",
    "TRASERA",
    "LATERAL_IZQUIERDO",
    "LATERAL_DERECHO",
    "INTERIOR",
}

LADOS_FOTO_VALIDOS = LADOS_FOTO_REQUERIDOS | {"EXTRA"}



class FotoVehiculoSchema(BaseModel):
    """
    Payload de entrada para una foto del vehículo.

    Por ahora no se sube el archivo real; se registran metadatos/ruta.
    """

    lado: str
    url: str
    formato: str
    tamanio_bytes: int

    @field_validator("lado")
    @classmethod
    def validar_lado(cls, v: str) -> str:
        """
        Normaliza y valida el lado fotografiado del vehículo.

        Acepta los cuatro lados obligatorios (FRENTE, TRASERA, LATERAL_*)
        y el lado EXTRA para fotos adicionales agregadas después del alta.
        """
        valor = v.strip().upper()
        if valor not in LADOS_FOTO_VALIDOS:
            raise ValueError("Lado de foto invalido")
        return valor

    @field_validator("url")
    @classmethod
    def validar_url(cls, v: str) -> str:
        """Valida que la URL/ruta de la foto no esté vacía."""
        if not v or not v.strip():
            raise ValueError("Campo obligatorio")
        return v.strip()

    @field_validator("formato")
    @classmethod
    def validar_formato(cls, v: str) -> str:
        """CA3 — Valida formato de foto permitido."""
        formato = v.strip().lower()
        if formato not in FORMATOS_FOTO_PERMITIDOS:
            raise ValueError("Formato de foto invalido")
        return formato

    @field_validator("tamanio_bytes")
    @classmethod
    def validar_tamanio(cls, v: int) -> int:
        """CA3 — Valida tamaño máximo permitido para la foto."""
        if v <= 0:
            raise ValueError("Tamanio de foto invalido")
        if v > TAMANIO_MAXIMO_FOTO_BYTES:
            raise ValueError("Tamanio de foto excedido")
        return v

class ReemplazarFotoVehiculoSchema(BaseModel):
    """
    Payload para reemplazar la imagen de una foto ya asociada a un vehículo.
    No incluye `lado` porque se preserva el del registro original.
    """

    url: str
    formato: str
    tamanio_bytes: int

    @field_validator("url")
    @classmethod
    def validar_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Campo obligatorio")
        return v.strip()

    @field_validator("formato")
    @classmethod
    def validar_formato(cls, v: str) -> str:
        formato = v.strip().lower()
        if formato not in FORMATOS_FOTO_PERMITIDOS:
            raise ValueError("Formato de foto invalido")
        return formato

    @field_validator("tamanio_bytes")
    @classmethod
    def validar_tamanio(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Tamanio de foto invalido")
        if v > TAMANIO_MAXIMO_FOTO_BYTES:
            raise ValueError("Tamanio de foto excedido")
        return v


class FotoVehiculoPublicoSchema(BaseModel):
    """
    Respuesta pública de una foto asociada al vehículo.
    """

    id: uuid.UUID
    vehiculo_id: uuid.UUID
    lado: str
    url: str
    formato: str
    tamanio_bytes: int

    model_config = {"from_attributes": True}

class VehiculoBaseSchema(BaseModel):
    """
    Datos esenciales para el alta inicial de un vehículo.

    Este schema representa únicamente la carga inicial de características
    y fotos. La documentación legal del vehículo se cargará en otro flujo.
    """

    marca: str
    modelo: str
    anio: int
    tipo_transmision: str
    capacidad: int
    categoria: str
    tipo_combustible: str
    pets_friendly: bool
    fotos: list[FotoVehiculoSchema]

    @field_validator(
        "marca",
        "modelo",
        "tipo_transmision",
        "categoria",
        "tipo_combustible",
    )
    @classmethod
    def validar_campo_obligatorio(cls, valor: str) -> str:
        if not valor or not valor.strip():
            raise ValueError("Campo obligatorio")

        return valor

    @field_validator("capacidad")
    @classmethod
    def validar_capacidad(cls, valor: int) -> int:
        if valor <= 0:
            raise ValueError("Capacidad invalida")

        return valor

    @field_validator("anio")
    @classmethod
    def validar_anio(cls, valor: int) -> int:
        from datetime import datetime

        anio_actual = datetime.now().year

        if valor < 1990 or valor > anio_actual:
            raise ValueError("Anio del auto invalido")

        return valor

    @model_validator(mode="after")
    def validar_fotos_requeridas(self):
        lados_recibidos = {foto.lado for foto in self.fotos}

        if not LADOS_FOTO_REQUERIDOS.issubset(lados_recibidos):
            raise ValueError("Cantidad minima de fotos requerida")

        return self

class RegistroVehiculoSchema(VehiculoBaseSchema):
    """
    Payload de servicio para registrar un vehículo.
    """

    propietario_id: uuid.UUID

class RegistroVehiculoPayloadSchema(VehiculoBaseSchema):
    """
    Payload HTTP para registrar un vehículo.

    No incluye propietario_id porque se recibe desde la URL del endpoint
    temporal POST /usuarios/{propietario_id}/vehiculos.
    """
    pass

class VehiculoPublicoSchema(BaseModel):
    """
    Respuesta pública del vehículo registrado.
    """

    id: uuid.UUID
    propietario_id: uuid.UUID
    marca: str
    modelo: str
    anio: int
    tipo_transmision: str
    capacidad: int
    categoria: str
    tipo_combustible: str
    pets_friendly: bool
    estado_registro: str
    motivo_rechazo: str | None = None
    fotos: list[FotoVehiculoPublicoSchema]
    precio_por_dia: Decimal | None = None
    disponible: bool = False

    model_config = {"from_attributes": True}

class DocumentacionVehiculoSchema(BaseModel):
    """
    Payload de entrada para cargar documentación legal del vehículo.

    Este flujo es posterior al alta inicial del vehículo.
    """

    patente: str
    chasis: str
    motor: str
    titular: str
    cedula: str
    poliza: str
    vtv: str
    estacion: str
    telefono: str
    descripcion: str | None = None

    @field_validator(
        "patente",
        "chasis",
        "motor",
        "titular",
        "cedula",
        "poliza",
        "vtv",
        "estacion",
        "telefono",
    )
    @classmethod
    def validar_campo_obligatorio(cls, valor: str) -> str:
        if not valor or not valor.strip():
            raise ValueError("Campo obligatorio")

        return valor.strip()

    @field_validator("descripcion")
    @classmethod
    def normalizar_descripcion(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        valor = valor.strip()
        return valor or None

class VehiculoDocumentacionResponseSchema(BaseModel):
    """
    Respuesta de documentación legal cargada para un vehículo.
    """

    id: uuid.UUID
    patente: str | None = None
    chasis: str | None = None
    motor: str | None = None
    titular: str | None = None
    cedula: str | None = None
    poliza: str | None = None
    vtv: str | None = None
    estacion: str | None = None
    telefono: str | None = None
    descripcion: str | None = None
    estado_registro: str

    model_config = {"from_attributes": True}

class DefinirPrecioVehiculoSchema(BaseModel):
    """
    Payload de entrada para definir la tarifa diaria de un vehículo.

    US 5D — Alcance:
        - solo precio por día
        - sin descuentos
        - sin comisión
        - sin precio dinámico
        - sin moneda múltiple
        - sin precio semanal/mensual
    """

    precio_por_dia: Decimal

    @field_validator("precio_por_dia")
    @classmethod
    def validar_precio_por_dia(cls, v: Decimal) -> Decimal:
        """CA1 — Rechaza tarifas diarias iguales o menores a cero."""
        if v <= 0:
            raise ValueError("Precio por dia invalido")
        return v

class PrecioVehiculoResponseSchema(BaseModel):
    """
    Respuesta pública de la US 5D luego de definir la tarifa diaria.
    """

    id: uuid.UUID
    precio_por_dia: Decimal

    model_config = {
        "from_attributes": True,
    }

class CambiarDisponibilidadSchema(BaseModel):
    """
    Payload de entrada para cambiar la disponibilidad del vehículo (US 9D).
    """
    disponible: bool

class DisponibilidadVehiculoResponseSchema(BaseModel):
    """
    Respuesta pública de la US 9D luego de cambiar la disponibilidad.
    """
    id: uuid.UUID
    disponible: bool

    model_config = {
        "from_attributes": True,
    }

class ActualizarVehiculoPayloadSchema(VehiculoBaseSchema):
    """
    Payload HTTP para actualizar las características y fotos de un vehículo.
    Hereda la validación de `VehiculoBaseSchema`.
    Incluye datos de documentación que pueden actualizarse posteriormente.
    """
    patente: str | None = None
    chasis: str | None = None
    motor: str | None = None
    titular: str | None = None
    estacion: str | None = None
    telefono: str | None = None
