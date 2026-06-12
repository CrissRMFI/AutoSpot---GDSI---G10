"""
Servicio de negocio — US 15D: Dashboard de ganancias generales.
"""
from datetime import datetime, timezone
from decimal import Decimal
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.reserva import Reserva
from app.models.vehiculo import Vehiculo
from app.schemas.ganancias import GananciasGeneralesResponseSchema, PeriodoGanancias
from app.services.reglas_financieras import (
    PORCENTAJE_COMISION_PLATAFORMA,
    PORCENTAJE_GANANCIA_PROPIETARIO,
    calcular_desglose_ganancias,
    calcular_variacion_porcentual,
    cuantizar_monto,
)


ZONA_REPORTE = ZoneInfo("America/Argentina/Buenos_Aires")


def _inicio_mes(fecha: datetime) -> datetime:
    return fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _sumar_meses(fecha: datetime, meses: int) -> datetime:
    mes_total = fecha.month - 1 + meses
    anio = fecha.year + mes_total // 12
    mes = mes_total % 12 + 1
    return fecha.replace(year=anio, month=mes, day=1)


def _inicio_anio(fecha: datetime) -> datetime:
    return fecha.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def obtener_rangos_periodo(
    periodo: PeriodoGanancias,
    ahora: datetime | None = None,
) -> tuple[datetime, datetime, datetime, datetime]:
    """
    Calcula el rango principal y su rango de comparación.

    Los límites se calculan en la zona horaria operativa local, porque los filtros
    que ve el propietario son de calendario ("este mes", "año actual").
    """
    referencia = ahora or datetime.now(timezone.utc)
    referencia_local = referencia.astimezone(ZONA_REPORTE)

    if periodo == "este_mes":
        desde = _inicio_mes(referencia_local)
        hasta = _sumar_meses(desde, 1)
        desde_comparacion = _sumar_meses(desde, -1)
        hasta_comparacion = desde
    elif periodo == "mes_anterior":
        hasta = _inicio_mes(referencia_local)
        desde = _sumar_meses(hasta, -1)
        desde_comparacion = _sumar_meses(desde, -1)
        hasta_comparacion = desde
    elif periodo == "anio_actual":
        desde = _inicio_anio(referencia_local)
        hasta = desde.replace(year=desde.year + 1)
        desde_comparacion = desde.replace(year=desde.year - 1)
        hasta_comparacion = desde
    else:
        raise ValueError("Periodo de ganancias invalido")

    return desde, hasta, desde_comparacion, hasta_comparacion


def _totales_periodo(
    db: Session,
    propietario_id: uuid.UUID,
    desde: datetime,
    hasta: datetime,
) -> tuple[Decimal, int]:
    total, cantidad = (
        db.query(
            func.coalesce(func.sum(Reserva.monto_total), Decimal("0.00")),
            func.count(Reserva.id),
        )
        .join(Vehiculo, Vehiculo.id == Reserva.vehiculo_id)
        .filter(
            Vehiculo.propietario_id == propietario_id,
            Reserva.estado == "FINALIZADA",
            Reserva.fecha_devolucion_real.isnot(None),
            Reserva.fecha_devolucion_real >= desde,
            Reserva.fecha_devolucion_real < hasta,
        )
        .one()
    )

    return cuantizar_monto(Decimal(total or 0)), int(cantidad or 0)


def obtener_ganancias_generales_propietario(
    db: Session,
    propietario_id: uuid.UUID,
    periodo: PeriodoGanancias,
    ahora: datetime | None = None,
) -> GananciasGeneralesResponseSchema:
    """Obtiene el resumen consolidado de ingresos del propietario."""
    desde, hasta, desde_comparacion, hasta_comparacion = obtener_rangos_periodo(
        periodo=periodo,
        ahora=ahora,
    )

    ingreso_bruto, reservas_finalizadas = _totales_periodo(
        db=db,
        propietario_id=propietario_id,
        desde=desde,
        hasta=hasta,
    )
    ingreso_comparacion, reservas_comparacion = _totales_periodo(
        db=db,
        propietario_id=propietario_id,
        desde=desde_comparacion,
        hasta=hasta_comparacion,
    )

    desglose = calcular_desglose_ganancias(ingreso_bruto)
    porcentaje_variacion, direccion_variacion = calcular_variacion_porcentual(
        actual=ingreso_bruto,
        comparacion=ingreso_comparacion,
    )

    return GananciasGeneralesResponseSchema(
        periodo=periodo,
        fecha_desde=desde,
        fecha_hasta=hasta,
        fecha_desde_comparacion=desde_comparacion,
        fecha_hasta_comparacion=hasta_comparacion,
        ingreso_bruto=desglose["ingreso_bruto"],
        comision_plataforma=desglose["comision_plataforma"],
        ganancia_neta=desglose["ganancia_neta"],
        ingreso_bruto_comparacion=ingreso_comparacion,
        porcentaje_variacion=porcentaje_variacion,
        direccion_variacion=direccion_variacion,
        reservas_finalizadas=reservas_finalizadas,
        reservas_finalizadas_comparacion=reservas_comparacion,
        porcentaje_comision_plataforma=PORCENTAJE_COMISION_PLATAFORMA,
        porcentaje_ganancia_propietario=PORCENTAJE_GANANCIA_PROPIETARIO,
    )
