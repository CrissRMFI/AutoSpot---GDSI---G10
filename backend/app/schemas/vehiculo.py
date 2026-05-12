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


class RegistroVehiculoSchema(BaseModel):
    """
    Payload de entrada para registrar características y fotos de un vehículo.
    """

    propietario_id: uuid.UUID
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
    def validar_campo_obligatorio_texto(cls, v: str) -> str:
        """CA1 — Rechaza campos de texto obligatorios vacíos."""
        if not v or not v.strip():
            raise ValueError("Campo obligatorio")
        return v.strip()

    @field_validator("anio")
    @classmethod
    def validar_anio(cls, v: int) -> int:
        """CA2 — Valida que el año esté dentro del rango permitido."""
        anio_actual = datetime.now().year
        if v > anio_actual:
            raise ValueError("Anio del auto invalido")
        if v < ANIO_MINIMO_PERMITIDO:
            raise ValueError("Anio del auto invalido")
        return v

    @field_validator("capacidad")
    @classmethod
    def validar_capacidad(cls, v: int) -> int:
        """CA1 — Valida que la capacidad sea positiva."""
        if v <= 0:
            raise ValueError("Capacidad invalida")
        return v

    @model_validator(mode="after")
    def validar_marca_modelo(self):
        """
        CA4 — Valida que la combinación marca/modelo exista en el catálogo.
        """
        modelos_validos = CATALOGO_MARCA_MODELO.get(self.marca)

        if modelos_validos is None or self.modelo not in modelos_validos:
            raise ValueError("Combinacion marca modelo inexistente")

        return self

    @model_validator(mode="after")
    def validar_fotos_requeridas(self):
        """
        CA5 — Valida que existan al menos 4 fotos, una por cada lado requerido.
        """
        lados = {foto.lado for foto in self.fotos}

        if len(self.fotos) < 4 or lados != LADOS_FOTO_REQUERIDOS:
            raise ValueError("Cantidad minima de fotos requerida")

        return self


class FotoVehiculoPublicoSchema(BaseModel):
    """
    Respuesta pública de una foto de vehículo.
    """

    id: uuid.UUID
    vehiculo_id: uuid.UUID
    lado: str
    url: str
    formato: str
    tamanio_bytes: int

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}
