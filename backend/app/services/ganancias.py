"""
Servicio de negocio — Dashboards de ganancias para propietarios.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.exceptions import VehiculoNoEncontradoError
from app.models.reserva import Reserva
from app.models.vehiculo import Vehiculo
from app.schemas.ganancias import (
    GananciasGeneralesResponseSchema,
    GananciasVehiculoResponseSchema,
    PeriodoGanancias,
    PuntoEvolucionGananciasSchema,
)
from app.services.reglas_financieras import (
    PORCENTAJE_COMISION_PLATAFORMA,
    PORCENTAJE_GANANCIA_PROPIETARIO,
    calcular_desglose_ganancias,
    calcular_variacion_porcentual,
    cuantizar_monto,
)


ZONA_REPORTE = ZoneInfo("America/Argentina/Buenos_Aires")
DIAS_CENTAVOS = Decimal("0.01")
MESES_ABREVIADOS = (
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
)
DIAS_SEMANA_ABREVIADOS = ("Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom")


def _inicio_mes(fecha: datetime) -> datetime:
    return fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _inicio_semana(fecha: datetime) -> datetime:
    inicio_dia = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
    return inicio_dia - timedelta(days=inicio_dia.weekday())


def _sumar_meses(fecha: datetime, meses: int) -> datetime:
    mes_total = fecha.month - 1 + meses
    anio = fecha.year + mes_total // 12
    mes = mes_total % 12 + 1
    return fecha.replace(year=anio, month=mes, day=1)


def _inicio_anio(fecha: datetime) -> datetime:
    return fecha.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def _decimal_dias(inicio: datetime, fin: datetime) -> Decimal:
    segundos = max((fin - inicio).total_seconds(), 0)
    dias = Decimal(str(segundos)) / Decimal("86400")
    return dias.quantize(DIAS_CENTAVOS, rounding=ROUND_HALF_UP)


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

    if periodo == "esta_semana":
        desde = _inicio_semana(referencia_local)
        hasta = desde + timedelta(days=7)
        desde_comparacion = desde - timedelta(days=7)
        hasta_comparacion = desde
    elif periodo == "este_mes":
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


def _buckets_evolucion_periodo(
    periodo: PeriodoGanancias,
    desde: datetime,
    hasta: datetime,
) -> list[tuple[str, str, datetime, datetime]]:
    if periodo == "esta_semana":
        return [
            (
                dia.strftime("%Y-%m-%d"),
                DIAS_SEMANA_ABREVIADOS[index],
                dia,
                dia + timedelta(days=1),
            )
            for index, dia in enumerate(
                desde + timedelta(days=offset) for offset in range(7)
            )
        ]

    if periodo in {"este_mes", "mes_anterior"}:
        buckets = []
        actual = desde
        numero_semana = 1
        while actual < hasta:
            fin = min(actual + timedelta(days=7), hasta)
            buckets.append(
                (
                    actual.strftime("%Y-%m-%d"),
                    f"Sem {numero_semana}",
                    actual,
                    fin,
                )
            )
            actual = fin
            numero_semana += 1
        return buckets

    if periodo == "anio_actual":
        buckets = []
        actual = desde
        while actual < hasta:
            fin = _sumar_meses(actual, 1)
            buckets.append(
                (
                    actual.strftime("%Y-%m"),
                    MESES_ABREVIADOS[actual.month - 1],
                    actual,
                    fin,
                )
            )
            actual = fin
        return buckets

    raise ValueError("Periodo de ganancias invalido")


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


def _totales_periodo_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    desde: datetime,
    hasta: datetime,
) -> tuple[Decimal, int]:
    total, cantidad = (
        db.query(
            func.coalesce(func.sum(Reserva.monto_total), Decimal("0.00")),
            func.count(Reserva.id),
        )
        .filter(
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.estado == "FINALIZADA",
            Reserva.fecha_devolucion_real.isnot(None),
            Reserva.fecha_devolucion_real >= desde,
            Reserva.fecha_devolucion_real < hasta,
        )
        .one()
    )

    return cuantizar_monto(Decimal(total or 0)), int(cantidad or 0)


def _dias_alquilados_periodo_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    desde: datetime,
    hasta: datetime,
) -> Decimal:
    reservas = (
        db.query(Reserva)
        .filter(
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.estado == "FINALIZADA",
            Reserva.fecha_devolucion_real.isnot(None),
            Reserva.fecha_inicio < hasta,
            Reserva.fecha_devolucion_real > desde,
        )
        .all()
    )

    dias = Decimal("0.00")
    for reserva in reservas:
        inicio_uso = reserva.fecha_salida_real or reserva.fecha_inicio
        fin_uso = (
            reserva.fecha_devolucion_real
            or reserva.fecha_entrega_solicitada
            or reserva.fecha_fin
        )

        inicio_solapado = max(inicio_uso, desde)
        fin_solapado = min(fin_uso, hasta)
        if fin_solapado > inicio_solapado:
            dias += _decimal_dias(inicio_solapado, fin_solapado)

    return dias.quantize(DIAS_CENTAVOS, rounding=ROUND_HALF_UP)


def _evolucion_periodo_general(
    db: Session,
    propietario_id: uuid.UUID,
    periodo: PeriodoGanancias,
    desde: datetime,
    hasta: datetime,
) -> list[PuntoEvolucionGananciasSchema]:
    evolucion = []
    for clave, etiqueta, bucket_desde, bucket_hasta in _buckets_evolucion_periodo(
        periodo=periodo,
        desde=desde,
        hasta=hasta,
    ):
        ingreso_bruto, reservas_finalizadas = _totales_periodo(
            db=db,
            propietario_id=propietario_id,
            desde=bucket_desde,
            hasta=bucket_hasta,
        )
        desglose = calcular_desglose_ganancias(ingreso_bruto)
        evolucion.append(
            PuntoEvolucionGananciasSchema(
                clave=clave,
                etiqueta=etiqueta,
                fecha_desde=bucket_desde,
                fecha_hasta=bucket_hasta,
                ingreso_bruto=desglose["ingreso_bruto"],
                comision_plataforma=desglose["comision_plataforma"],
                ganancia_neta=desglose["ganancia_neta"],
                reservas_finalizadas=reservas_finalizadas,
            )
        )
    return evolucion


def _evolucion_periodo_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    periodo: PeriodoGanancias,
    desde: datetime,
    hasta: datetime,
) -> list[PuntoEvolucionGananciasSchema]:
    evolucion = []
    for clave, etiqueta, bucket_desde, bucket_hasta in _buckets_evolucion_periodo(
        periodo=periodo,
        desde=desde,
        hasta=hasta,
    ):
        ingreso_bruto, reservas_finalizadas = _totales_periodo_vehiculo(
            db=db,
            vehiculo_id=vehiculo_id,
            desde=bucket_desde,
            hasta=bucket_hasta,
        )
        desglose = calcular_desglose_ganancias(ingreso_bruto)
        dias_alquilados = _dias_alquilados_periodo_vehiculo(
            db=db,
            vehiculo_id=vehiculo_id,
            desde=bucket_desde,
            hasta=bucket_hasta,
        )
        dias_disponibles = _decimal_dias(bucket_desde, bucket_hasta)
        tasa_ocupacion = Decimal("0.00")
        if dias_disponibles > 0:
            tasa_ocupacion = (
                dias_alquilados / dias_disponibles * Decimal("100")
            ).quantize(DIAS_CENTAVOS, rounding=ROUND_HALF_UP)

        evolucion.append(
            PuntoEvolucionGananciasSchema(
                clave=clave,
                etiqueta=etiqueta,
                fecha_desde=bucket_desde,
                fecha_hasta=bucket_hasta,
                ingreso_bruto=desglose["ingreso_bruto"],
                comision_plataforma=desglose["comision_plataforma"],
                ganancia_neta=desglose["ganancia_neta"],
                reservas_finalizadas=reservas_finalizadas,
                dias_alquilados=dias_alquilados,
                dias_disponibles=dias_disponibles,
                tasa_ocupacion=tasa_ocupacion,
            )
        )
    return evolucion


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
        evolucion_periodo=_evolucion_periodo_general(
            db=db,
            propietario_id=propietario_id,
            periodo=periodo,
            desde=desde,
            hasta=hasta,
        ),
    )


def obtener_ganancias_vehiculo_propietario(
    db: Session,
    propietario_id: uuid.UUID,
    vehiculo_id: uuid.UUID,
    periodo: PeriodoGanancias,
    ahora: datetime | None = None,
) -> GananciasVehiculoResponseSchema:
    """Obtiene ingresos y métricas de uso de un vehículo del propietario."""
    vehiculo = (
        db.query(Vehiculo)
        .filter(
            Vehiculo.id == vehiculo_id,
            Vehiculo.propietario_id == propietario_id,
        )
        .first()
    )
    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    desde, hasta, desde_comparacion, hasta_comparacion = obtener_rangos_periodo(
        periodo=periodo,
        ahora=ahora,
    )

    ingreso_bruto, reservas_finalizadas = _totales_periodo_vehiculo(
        db=db,
        vehiculo_id=vehiculo_id,
        desde=desde,
        hasta=hasta,
    )
    ingreso_comparacion, reservas_comparacion = _totales_periodo_vehiculo(
        db=db,
        vehiculo_id=vehiculo_id,
        desde=desde_comparacion,
        hasta=hasta_comparacion,
    )
    dias_alquilados = _dias_alquilados_periodo_vehiculo(
        db=db,
        vehiculo_id=vehiculo_id,
        desde=desde,
        hasta=hasta,
    )
    dias_disponibles = _decimal_dias(desde, hasta)
    tasa_ocupacion = Decimal("0.00")
    if dias_disponibles > 0:
        tasa_ocupacion = (
            dias_alquilados / dias_disponibles * Decimal("100")
        ).quantize(DIAS_CENTAVOS, rounding=ROUND_HALF_UP)

    desglose = calcular_desglose_ganancias(ingreso_bruto)
    porcentaje_variacion, direccion_variacion = calcular_variacion_porcentual(
        actual=ingreso_bruto,
        comparacion=ingreso_comparacion,
    )

    return GananciasVehiculoResponseSchema(
        vehiculo_id=str(vehiculo.id),
        patente=vehiculo.patente,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        categoria=vehiculo.categoria,
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
        dias_alquilados=dias_alquilados,
        dias_disponibles=dias_disponibles,
        tasa_ocupacion=tasa_ocupacion,
        porcentaje_comision_plataforma=PORCENTAJE_COMISION_PLATAFORMA,
        porcentaje_ganancia_propietario=PORCENTAJE_GANANCIA_PROPIETARIO,
        evolucion_periodo=_evolucion_periodo_vehiculo(
            db=db,
            vehiculo_id=vehiculo_id,
            periodo=periodo,
            desde=desde,
            hasta=hasta,
        ),
    )
