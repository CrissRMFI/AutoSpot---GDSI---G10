"""
Lógica de negocio para la gestión de alquileres.
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from math import ceil, floor
import secrets
import uuid

from sqlalchemy import case
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.exceptions import (
    MotivoRechazoRequeridoError,
    ReservaActivaExistenteError,
    ReservaCodigoYaVerificadoError,
    ReservaNoEnCursoError,
    ReservaNoEncontradaError,
    ReservaNoEntregableError,
    ReservaNoRechazableError,
    ReservaSinCheckinAprobadoError,
    VehiculoNoDisponibleParaReservaError,
    VehiculoNoEncontradoError,
)
from app.models.checkin_vehiculo import CheckinVehiculo
from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.alquiler import CrearReservaPayloadSchema
from app.services.notificacion import (
    RECURSO_RESERVA,
    TIPO_AUTO_DEVUELTO,
    cerrar_notificaciones_reserva_pendiente_verificacion,
    cerrar_notificaciones_de_reserva_por_tipo,
    crear_notificacion_usuario,
    crear_notificacion_reserva_aprobada,
    crear_notificacion_reserva_rechazada,
    crear_notificaciones_reserva_pendiente_verificacion,
)


ESTADOS_RESERVA_ACTIVA = {
    "CONFIRMADA",
    "CODIGO_GENERADO",
    "VERIFICADA",
    "EN_CURSO",
    "ENTREGA_SOLICITADA",
    "DEVUELTO",
    "CHECKOUT_PENDIENTE",
}
ESTADOS_RESERVA_BLOQUEADA_PARA_ENTREGA = {
    "CANCELADA",
    "FINALIZADA",
    "RECHAZADA",
    "EN_CURSO",
    "ENTREGA_SOLICITADA",
    "DEVUELTO",
    "CHECKOUT_PENDIENTE",
}
ESTADOS_RESERVA_RECHAZABLE = {"CONFIRMADA", "CODIGO_GENERADO"}

def calcular_tiempo_alquiler(inicio: datetime, fin: datetime) -> dict:
    """
    Calcula la duración exacta de un periodo de alquiler en días y horas.
    
    Reglas de negocio:
      - CA1: El tiempo mínimo de alquiler es de 1 día (24 horas).
      - CA2: Calcula la duración en días y horas exactas.
      
    Args:
        inicio (datetime): Fecha y hora de inicio.
        fin (datetime): Fecha y hora de fin.
        
    Returns:
        dict: Diccionario con 'dias' y 'horas'.
        
    Raises:
        ValueError: Si la duración es menor a 1 día o las fechas son incoherentes.
    """
    if fin < inicio:
        raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        
    diferencia = fin - inicio
    
    # 86400 segundos = 24 horas
    if diferencia.total_seconds() < 86400:
        raise ValueError("El tiempo minimo de alquiler es de 1 dia")
        
    dias = diferencia.days
    segundos_restantes = diferencia.seconds
    horas = floor(segundos_restantes / 3600)
    
    return {
        "dias": dias,
        "horas": horas
    }


def _generar_codigo_reserva(db: Session) -> str:
    """Genera un código corto único para presentar en la estación."""
    for _ in range(10):
        codigo = f"AS-{secrets.token_hex(3).upper()}"
        existe = db.query(Reserva).filter(Reserva.codigo == codigo).first()
        if existe is None:
            return codigo
    raise RuntimeError("No se pudo generar un código de reserva único")


def _calcular_monto_total(precio_por_dia: Decimal, dias: int, horas: int) -> Decimal:
    """Calcula el monto proporcional al período reservado."""
    duracion_en_dias = Decimal(dias) + (Decimal(horas) / Decimal(24))
    monto = Decimal(precio_por_dia) * duracion_en_dias
    return monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def crear_reserva_con_codigo(
    db: Session,
    schema: CrearReservaPayloadSchema,
    conductor_id: uuid.UUID,
) -> Reserva:
    """
    Crea una reserva confirmada y genera su código de retiro (US 14C).

    Para esta historia se bloquea el vehículo y se emite el código de retiro.
    """
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == schema.vehiculo_id).first()
    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    reserva_activa = (
        db.query(Reserva)
        .filter(
            Reserva.vehiculo_id == schema.vehiculo_id,
            Reserva.estado.in_(ESTADOS_RESERVA_ACTIVA),
        )
        .first()
    )
    if reserva_activa is not None:
        raise ReservaActivaExistenteError()

    if (
        vehiculo.estado_registro != "HABILITADO"
        or not vehiculo.disponible
        or vehiculo.precio_por_dia is None
        or vehiculo.precio_por_dia <= 0
        or not vehiculo.estacion
    ):
        raise VehiculoNoDisponibleParaReservaError()

    duracion = calcular_tiempo_alquiler(schema.fecha_inicio, schema.fecha_fin)
    codigo = _generar_codigo_reserva(db)

    reserva = Reserva(
        vehiculo_id=schema.vehiculo_id,
        conductor_id=conductor_id,
        codigo=codigo,
        estado="CONFIRMADA",
        monto_total=_calcular_monto_total(
            precio_por_dia=vehiculo.precio_por_dia,
            dias=duracion["dias"],
            horas=duracion["horas"],
        ),
        fecha_inicio=schema.fecha_inicio,
        fecha_fin=schema.fecha_fin,
        estacion_retiro=vehiculo.estacion,
    )

    vehiculo.disponible = False
    db.add(reserva)
    db.flush()
    crear_notificaciones_reserva_pendiente_verificacion(db=db, reserva=reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def listar_reservas_de_conductor(
    db: Session,
    conductor_id: uuid.UUID,
) -> list[Reserva]:
    """Lista las reservas del conductor autenticado, de más nueva a más antigua."""
    return (
        db.query(Reserva)
        .options(joinedload(Reserva.vehiculo).joinedload(Vehiculo.fotos))
        .filter(Reserva.conductor_id == conductor_id)
        .order_by(Reserva.created_at.desc())
        .all()
    )


def obtener_reserva_admin(
    db: Session,
    reserva_id: uuid.UUID,
) -> Reserva:
    """Obtiene una reserva con vehículo/conductor para la pantalla admin de US 5R."""
    reserva = (
        db.query(Reserva)
        .options(
            joinedload(Reserva.vehiculo).joinedload(Vehiculo.fotos),
            joinedload(Reserva.conductor),
        )
        .filter(Reserva.id == reserva_id)
        .first()
    )
    if reserva is None:
        raise ReservaNoEncontradaError()
    return reserva


def buscar_reserva_por_codigo(
    db: Session,
    codigo_reserva: str,
) -> Reserva:
    """
    Lookup admin de una reserva por código sin marcar verificación.

    Permite consultar el detalle antes de decidir aprobar o rechazar.
    """
    codigo = (codigo_reserva or "").strip()
    reserva = (
        db.query(Reserva)
        .options(
            joinedload(Reserva.vehiculo).joinedload(Vehiculo.fotos),
            joinedload(Reserva.conductor),
        )
        .filter(Reserva.codigo == codigo)
        .first()
    )
    if reserva is None:
        raise ReservaNoEncontradaError()
    return reserva


def obtener_datos_personales_de_conductor(
    db: Session,
    conductor_id: uuid.UUID,
) -> DatosPersonalesUsuario | None:
    """Devuelve DNI/nombre/apellido si el conductor ya completó datos personales."""
    return (
        db.query(DatosPersonalesUsuario)
        .filter(DatosPersonalesUsuario.usuario_id == conductor_id)
        .first()
    )


def motivo_bloqueo_entrega(reserva: Reserva) -> str | None:
    """Indica por qué una reserva no puede pasar al flujo de entrega."""
    estado = (reserva.estado or "").upper()
    if estado in ESTADOS_RESERVA_BLOQUEADA_PARA_ENTREGA:
        return f"La reserva está {estado.lower()}."

    if reserva.fecha_inicio < datetime.now(timezone.utc):
        return "La fecha de inicio de la reserva ya expiró."

    return None


def verificar_codigo_reserva(
    db: Session,
    codigo_reserva: str,
) -> Reserva:
    """
    Verifica el código de una reserva y lo invalida para futuros usos.

    El código no expira por tiempo; su validez termina con la primera
    verificación exitosa.
    """
    codigo = (codigo_reserva or "").strip()
    reserva = (
        db.query(Reserva)
        .filter(Reserva.codigo == codigo)
        .with_for_update()
        .first()
    )

    if reserva is None:
        raise ReservaNoEncontradaError()

    if reserva.codigo_verificado_at is not None:
        raise ReservaCodigoYaVerificadoError()

    if motivo_bloqueo_entrega(reserva) is None:
        reserva.codigo_verificado_at = datetime.now(timezone.utc)
        reserva.estado = "VERIFICADA"
        cerrar_notificaciones_reserva_pendiente_verificacion(db=db, reserva=reserva)
        crear_notificacion_reserva_aprobada(db=db, reserva=reserva)

    db.commit()
    db.refresh(reserva)
    return reserva


def rechazar_reserva(
    db: Session,
    reserva_id: uuid.UUID,
    motivo: str,
) -> Reserva:
    """
    Rechaza una reserva pendiente: marca el estado, guarda el motivo,
    libera el vehículo al catálogo y notifica al conductor.
    """
    motivo_limpio = (motivo or "").strip()
    if not motivo_limpio:
        raise MotivoRechazoRequeridoError()

    reserva = (
        db.query(Reserva)
        .filter(Reserva.id == reserva_id)
        .with_for_update()
        .first()
    )

    if reserva is None:
        raise ReservaNoEncontradaError()

    estado_actual = (reserva.estado or "").upper()
    if (
        estado_actual not in ESTADOS_RESERVA_RECHAZABLE
        or reserva.codigo_verificado_at is not None
    ):
        raise ReservaNoRechazableError()

    reserva.estado = "RECHAZADA"
    reserva.motivo_rechazo = motivo_limpio

    if reserva.vehiculo is not None:
        reserva.vehiculo.disponible = True

    cerrar_notificaciones_reserva_pendiente_verificacion(db=db, reserva=reserva)
    crear_notificacion_reserva_rechazada(db=db, reserva=reserva, motivo=motivo_limpio)

    db.commit()
    db.refresh(reserva)
    return reserva


def _existe_checkin_aprobado(db: Session, reserva_id: uuid.UUID) -> bool:
    """True si la reserva tiene un check-in en estado APROBADO."""
    checkin = (
        db.query(CheckinVehiculo)
        .filter(CheckinVehiculo.reserva_id == reserva_id)
        .first()
    )
    return checkin is not None and (checkin.estado or "").upper() == "APROBADO"


def registrar_salida(db: Session, reserva_id: uuid.UUID) -> Reserva:
    """
    Registra la salida del auto y deja el alquiler EN_CURSO.

    Precondiciones: la reserva debe estar VERIFICADA (código verificado) y el
    check-in del conductor debe estar APROBADO.
    """
    reserva = (
        db.query(Reserva)
        .filter(Reserva.id == reserva_id)
        .with_for_update()
        .first()
    )
    if reserva is None:
        raise ReservaNoEncontradaError()

    if (reserva.estado or "").upper() != "VERIFICADA" or reserva.codigo_verificado_at is None:
        raise ReservaNoEntregableError()

    if not _existe_checkin_aprobado(db=db, reserva_id=reserva.id):
        raise ReservaSinCheckinAprobadoError()

    reserva.estado = "EN_CURSO"
    reserva.fecha_salida_real = datetime.now(timezone.utc)

    db.commit()
    db.refresh(reserva)
    return reserva


def _calcular_penalizacion(
    reserva: Reserva,
    fecha_devolucion: datetime,
) -> tuple[int | None, Decimal | None]:
    """
    Calcula minutos de retraso y penalización por devolución tardía.

    Regla (supuesto, ajustable): días de retraso redondeados hacia arriba
    multiplicados por la tarifa diaria del vehículo.
    """
    if fecha_devolucion <= reserva.fecha_fin:
        return None, None

    delta = fecha_devolucion - reserva.fecha_fin
    minutos = int(delta.total_seconds() // 60)

    precio_por_dia = reserva.vehiculo.precio_por_dia if reserva.vehiculo else None
    if precio_por_dia is None or precio_por_dia <= 0:
        return minutos, None

    dias_retraso = ceil(delta.total_seconds() / 86400)
    monto = (Decimal(precio_por_dia) * Decimal(dias_retraso)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return minutos, monto


def registrar_entrada(db: Session, reserva_id: uuid.UUID) -> Reserva:
    """
    Registra la entrada/devolución del auto y deja el alquiler DEVUELTO.

    Aplica penalización automática si la devolución es posterior a la fecha
    de fin pactada.
    """
    reserva = (
        db.query(Reserva)
        .filter(Reserva.id == reserva_id)
        .with_for_update()
        .first()
    )
    if reserva is None:
        raise ReservaNoEncontradaError()

    if (reserva.estado or "").upper() != "ENTREGA_SOLICITADA":
        raise ReservaNoEnCursoError()

    ahora = datetime.now(timezone.utc)
    reserva.fecha_devolucion_real = ahora
    reserva.minutos_retraso, reserva.monto_penalizacion = _calcular_penalizacion(
        reserva=reserva,
        fecha_devolucion=ahora,
    )
    reserva.estado = "DEVUELTO"
    cerrar_notificaciones_de_reserva_por_tipo(
        db=db,
        reserva_id=reserva.id,
        tipos=[TIPO_AUTO_DEVUELTO],
    )

    db.commit()
    db.refresh(reserva)
    return reserva


def listar_reservas_para_entregar(db: Session) -> list[Reserva]:
    """
    Reservas listas para entregar (US 6R): VERIFICADA con check-in APROBADO,
    todavía no entregadas. Alimenta la pantalla de Entrega de autos.
    """
    return (
        db.query(Reserva)
        .join(CheckinVehiculo, CheckinVehiculo.reserva_id == Reserva.id)
        .filter(
            Reserva.estado == "VERIFICADA",
            CheckinVehiculo.estado == "APROBADO",
        )
        .options(
            joinedload(Reserva.vehiculo).joinedload(Vehiculo.fotos),
            joinedload(Reserva.conductor),
        )
        .order_by(Reserva.codigo_verificado_at.asc())
        .all()
    )


def listar_reservas_en_curso(db: Session) -> list[Reserva]:
    """Reservas EN_CURSO, para la pantalla de recepción (US 7R)."""
    return (
        db.query(Reserva)
        .options(
            joinedload(Reserva.vehiculo).joinedload(Vehiculo.fotos),
            joinedload(Reserva.conductor),
        )
        .filter(Reserva.estado == "EN_CURSO")
        .order_by(Reserva.fecha_salida_real.desc())
        .all()
    )


def listar_reservas_devueltas(db: Session) -> list[Reserva]:
    """
    Reservas DEVUELTO pendientes de checkout, para la pantalla de checkout. Una reserva pasa a FINALIZADA al registrarse su checkout, por lo
    que DEVUELTO implica que todavía no tiene checkout.
    """
    return (
        db.query(Reserva)
        .options(
            joinedload(Reserva.vehiculo).joinedload(Vehiculo.fotos),
            joinedload(Reserva.conductor),
        )
        .filter(Reserva.estado == "DEVUELTO")
        .order_by(Reserva.fecha_devolucion_real.desc())
        .all()
    )


def _notificar_admins(
    db: Session,
    tipo: str,
    titulo: str,
    mensaje: str,
    reserva: Reserva,
) -> None:
    """Crea una notificación para cada admin activo (no hace commit)."""
    admins = (
        db.query(Usuario)
        .filter(Usuario.rol == "ADMIN", Usuario.is_active.is_(True))
        .all()
    )
    for admin in admins:
        crear_notificacion_usuario(
            db=db,
            usuario_id=admin.id,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            recurso_tipo=RECURSO_RESERVA,
            recurso_id=reserva.id,
        )


def entregar_auto(
    db: Session,
    reserva_id: uuid.UUID,
    conductor_id: uuid.UUID,
) -> Reserva:
    """
    US 22C — El conductor avisa que entrega el auto: EN_CURSO → ENTREGA_SOLICITADA.

    Es solo un aviso (registra `fecha_entrega_solicitada` para auditoría). La
    fecha real de devolución y la penalización las fija el admin al registrar
    la entrada, antes del checkout.
    """
    reserva = (
        db.query(Reserva)
        .filter(Reserva.id == reserva_id)
        .with_for_update()
        .first()
    )
    if reserva is None or reserva.conductor_id != conductor_id:
        raise ReservaNoEncontradaError()

    if (reserva.estado or "").upper() != "EN_CURSO":
        raise ReservaNoEnCursoError()

    reserva.estado = "ENTREGA_SOLICITADA"
    reserva.fecha_entrega_solicitada = datetime.now(timezone.utc)

    _notificar_admins(
        db=db,
        tipo=TIPO_AUTO_DEVUELTO,
        titulo="Auto para recibir",
        mensaje=f"El conductor entregó el auto de la reserva {reserva.codigo}. Registrá la entrada.",
        reserva=reserva,
    )

    db.commit()
    db.refresh(reserva)
    return reserva


ESTADOS_ALQUILER = [
    "EN_CURSO",
    "ENTREGA_SOLICITADA",
    "DEVUELTO",
    "CHECKOUT_PENDIENTE",
    "FINALIZADA",
]
ESTADOS_RECEPCION = [
    "ENTREGA_SOLICITADA",
    "DEVUELTO",
    "CHECKOUT_PENDIENTE",
    "FINALIZADA",
]


def listar_mis_alquileres(
    db: Session,
    conductor_id: uuid.UUID,
    page: int,
    size: int,
) -> tuple[list[Reserva], int]:
    """Alquileres del conductor (paginado), activos primero y finalizados al final."""
    base = db.query(Reserva).filter(
        Reserva.conductor_id == conductor_id,
        Reserva.estado.in_(ESTADOS_ALQUILER),
    )
    total = base.count()
    items = (
        base.options(joinedload(Reserva.vehiculo).joinedload(Vehiculo.fotos))
        .order_by((Reserva.estado == "FINALIZADA"), Reserva.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return items, total


def obtener_alquiler_conductor(
    db: Session,
    reserva_id: uuid.UUID,
    conductor_id: uuid.UUID,
) -> Reserva:
    """Detalle de un alquiler propio del conductor."""
    reserva = (
        db.query(Reserva)
        .options(joinedload(Reserva.vehiculo).joinedload(Vehiculo.fotos))
        .filter(Reserva.id == reserva_id)
        .first()
    )
    if reserva is None or reserva.conductor_id != conductor_id:
        raise ReservaNoEncontradaError()
    return reserva


def listar_recepcion(
    db: Session,
    page: int,
    size: int,
) -> tuple[list[Reserva], int]:
    """
    Autos para recibir (paginado): primero los que requieren registrar entrada,
    luego los que requieren checkout y finalmente los ya procesados.
    """
    base = db.query(Reserva).filter(Reserva.estado.in_(ESTADOS_RECEPCION))
    total = base.count()
    items = (
        base.options(
            joinedload(Reserva.vehiculo).joinedload(Vehiculo.fotos),
            joinedload(Reserva.conductor),
        )
        .order_by(
            case(
                (Reserva.estado == "ENTREGA_SOLICITADA", 0),
                (Reserva.estado == "DEVUELTO", 1),
                (Reserva.estado == "CHECKOUT_PENDIENTE", 2),
                else_=3,
            ),
            Reserva.fecha_entrega_solicitada.desc(),
        )
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return items, total
