"""
Schemas Pydantic — Dashboards de ganancias para propietarios.
"""
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


PeriodoGanancias = Literal["esta_semana", "este_mes", "mes_anterior", "anio_actual"]


class GananciasGeneralesResponseSchema(BaseModel):
    """Resumen financiero consolidado para el propietario autenticado."""

    periodo: PeriodoGanancias
    fecha_desde: datetime
    fecha_hasta: datetime
    fecha_desde_comparacion: datetime
    fecha_hasta_comparacion: datetime
    fecha_imputacion: str = "fecha_devolucion_real"
    ingreso_bruto: Decimal
    comision_plataforma: Decimal
    ganancia_neta: Decimal
    ingreso_bruto_comparacion: Decimal
    porcentaje_variacion: Decimal | None = None
    direccion_variacion: str
    reservas_finalizadas: int
    reservas_finalizadas_comparacion: int
    porcentaje_comision_plataforma: Decimal
    porcentaje_ganancia_propietario: Decimal


class GananciasVehiculoResponseSchema(BaseModel):
    """Resumen financiero y de uso para una unidad del propietario."""

    vehiculo_id: str
    patente: str | None = None
    marca: str
    modelo: str
    categoria: str
    periodo: PeriodoGanancias
    fecha_desde: datetime
    fecha_hasta: datetime
    fecha_desde_comparacion: datetime
    fecha_hasta_comparacion: datetime
    ingreso_bruto: Decimal
    comision_plataforma: Decimal
    ganancia_neta: Decimal
    ingreso_bruto_comparacion: Decimal
    porcentaje_variacion: Decimal | None = None
    direccion_variacion: str
    reservas_finalizadas: int
    reservas_finalizadas_comparacion: int
    dias_alquilados: Decimal
    dias_disponibles: Decimal
    tasa_ocupacion: Decimal
    porcentaje_comision_plataforma: Decimal
    porcentaje_ganancia_propietario: Decimal
