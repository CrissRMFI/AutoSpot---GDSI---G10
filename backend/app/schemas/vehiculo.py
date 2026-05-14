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
}



# Catálogo inicial hardcodeado para US 1D.
# Más adelante puede reemplazarse por una tabla o servicio de catálogo.
CATALOGO_MARCA_MODELO = {
    "Toyota": {"Corolla", "Etios", "Hilux"},
    "Ford": {"Fiesta", "Focus", "Ranger"},
    "Volkswagen": {"Gol", "Polo", "Amarok"},
    "Chevrolet": {"Onix", "Cruze", "S10"},
    "Renault": {"Clio", "Sandero", "Kangoo"},
}


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
        """Normaliza y valida el lado fotografiado del vehículo."""
        valor = v.strip().upper()
        if valor not in LADOS_FOTO_REQUERIDOS:
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
        lados_requeridos = {
            "FRENTE",
            "TRASERA",
            "LATERAL_IZQUIERDO",
            "LATERAL_DERECHO",
        }

        lados_recibidos = {foto.lado for foto in self.fotos}

        if not lados_requeridos.issubset(lados_recibidos):
            raise ValueError("Cantidad minima de fotos requerida")

        return self

    @model_validator(mode="after")
    def validar_marca_modelo(self):
       modelos_validos = CATALOGO_MARCA_MODELO.get(self.marca)
       
       if modelos_validos is None or self.modelo not in modelos_validos:
        raise ValueError("Combinacion marca modelo inexistente")

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
    fotos: list[FotoVehiculoPublicoSchema]
    precio_por_dia: Decimal | None = None

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
