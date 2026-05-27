"""
Servicio de negocio — Notificaciones de usuario.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.exceptions import NotificacionNoEncontradaError
from app.models.notificacion import Notificacion
from app.models.vehiculo import Vehiculo


TIPO_VEHICULO_DOCUMENTACION_PENDIENTE = "VEHICULO_DOCUMENTACION_PENDIENTE"
TIPO_VEHICULO_HABILITADO = "VEHICULO_HABILITADO"
TIPO_VEHICULO_RECHAZADO = "VEHICULO_RECHAZADO"
RECURSO_VEHICULO = "VEHICULO"
ESTADO_VEHICULO_PENDIENTE_DOCUMENTACION = "PENDIENTE_DOCUMENTACION"


def _nombre_vehiculo(vehiculo: Vehiculo) -> str:
    return f"{vehiculo.marca} {vehiculo.modelo}".strip()


def _buscar_notificacion_vehiculo(
    db: Session,
    usuario_id: uuid.UUID,
    vehiculo_id: uuid.UUID,
    tipo: str,
) -> Notificacion | None:
    return (
        db.query(Notificacion)
        .filter(
            Notificacion.usuario_id == usuario_id,
            Notificacion.tipo == tipo,
            Notificacion.recurso_tipo == RECURSO_VEHICULO,
            Notificacion.recurso_id == vehiculo_id,
        )
        .first()
    )


def crear_notificacion_documentacion_pendiente(
    db: Session,
    vehiculo: Vehiculo,
) -> Notificacion:
    """
    Crea o reutiliza el recordatorio persistente de carga documental.

    No hace commit: el alta del vehículo y su notificación se persisten juntas.
    """
    existente = _buscar_notificacion_vehiculo(
        db=db,
        usuario_id=vehiculo.propietario_id,
        vehiculo_id=vehiculo.id,
        tipo=TIPO_VEHICULO_DOCUMENTACION_PENDIENTE,
    )
    if existente is not None:
        return existente

    nombre_vehiculo = _nombre_vehiculo(vehiculo)
    notificacion = Notificacion(
        usuario_id=vehiculo.propietario_id,
        tipo=TIPO_VEHICULO_DOCUMENTACION_PENDIENTE,
        titulo="Documentación pendiente",
        mensaje=f"Subí la documentación de tu {nombre_vehiculo} para enviarlo a revisión.",
        recurso_tipo=RECURSO_VEHICULO,
        recurso_id=vehiculo.id,
    )
    db.add(notificacion)
    return notificacion


def cerrar_notificacion_documentacion_pendiente(
    db: Session,
    vehiculo: Vehiculo,
) -> None:
    """
    Oculta el recordatorio documental cuando el vehículo ya no está pendiente.
    """
    notificacion = _buscar_notificacion_vehiculo(
        db=db,
        usuario_id=vehiculo.propietario_id,
        vehiculo_id=vehiculo.id,
        tipo=TIPO_VEHICULO_DOCUMENTACION_PENDIENTE,
    )
    if notificacion is not None and notificacion.vista_at is None:
        notificacion.vista_at = datetime.now(timezone.utc)


def sincronizar_notificaciones_documentacion_pendiente(
    db: Session,
    usuario_id: uuid.UUID,
) -> list[uuid.UUID]:
    """
    Garantiza un recordatorio activo por cada vehículo pendiente del usuario.

    Esto cubre vehículos creados antes de existir el módulo de notificaciones.
    """
    vehiculos_pendientes = (
        db.query(Vehiculo)
        .filter(
            Vehiculo.propietario_id == usuario_id,
            Vehiculo.estado_registro == ESTADO_VEHICULO_PENDIENTE_DOCUMENTACION,
        )
        .all()
    )
    ids_pendientes = [vehiculo.id for vehiculo in vehiculos_pendientes]

    hubo_cambios = False
    for vehiculo in vehiculos_pendientes:
        notificacion = _buscar_notificacion_vehiculo(
            db=db,
            usuario_id=usuario_id,
            vehiculo_id=vehiculo.id,
            tipo=TIPO_VEHICULO_DOCUMENTACION_PENDIENTE,
        )
        if notificacion is None:
            crear_notificacion_documentacion_pendiente(db=db, vehiculo=vehiculo)
            hubo_cambios = True

    query_resueltas = db.query(Notificacion).filter(
        Notificacion.usuario_id == usuario_id,
        Notificacion.tipo == TIPO_VEHICULO_DOCUMENTACION_PENDIENTE,
        Notificacion.recurso_tipo == RECURSO_VEHICULO,
        Notificacion.vista_at.is_(None),
    )
    if ids_pendientes:
        query_resueltas = query_resueltas.filter(
            Notificacion.recurso_id.notin_(ids_pendientes)
        )

    for notificacion in query_resueltas.all():
        notificacion.vista_at = datetime.now(timezone.utc)
        hubo_cambios = True

    if hubo_cambios:
        db.commit()

    return ids_pendientes


def crear_notificacion_resolucion_vehiculo(
    db: Session,
    vehiculo: Vehiculo,
    aprobada: bool,
    motivo_rechazo: str | None = None,
) -> Notificacion:
    """
    Crea el aviso para el propietario al aprobar o rechazar un vehículo.

    No hace commit: la resolución de la solicitud y la notificación deben
    persistirse en la misma transacción.
    """
    nombre_vehiculo = _nombre_vehiculo(vehiculo)

    if aprobada:
        notificacion = Notificacion(
            usuario_id=vehiculo.propietario_id,
            tipo=TIPO_VEHICULO_HABILITADO,
            titulo="Vehículo habilitado",
            mensaje=f"Tu {nombre_vehiculo} fue habilitado para operar en AutoSpot.",
            recurso_tipo=RECURSO_VEHICULO,
            recurso_id=vehiculo.id,
        )
    else:
        motivo = (motivo_rechazo or "Revisá la documentación cargada.").strip()
        notificacion = Notificacion(
            usuario_id=vehiculo.propietario_id,
            tipo=TIPO_VEHICULO_RECHAZADO,
            titulo="Vehículo rechazado",
            mensaje=f"Tu {nombre_vehiculo} fue rechazado. Motivo: {motivo}",
            recurso_tipo=RECURSO_VEHICULO,
            recurso_id=vehiculo.id,
        )

    db.add(notificacion)
    return notificacion


def listar_notificaciones_no_vistas(
    db: Session,
    usuario_id: uuid.UUID,
) -> list[Notificacion]:
    """
    Devuelve las notificaciones pendientes de lectura del usuario.
    """
    ids_pendientes = sincronizar_notificaciones_documentacion_pendiente(
        db=db,
        usuario_id=usuario_id,
    )
    query = db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id)

    visibilidad = Notificacion.vista_at.is_(None)
    if ids_pendientes:
        visibilidad = or_(
            visibilidad,
            and_(
                Notificacion.tipo == TIPO_VEHICULO_DOCUMENTACION_PENDIENTE,
                Notificacion.recurso_tipo == RECURSO_VEHICULO,
                Notificacion.recurso_id.in_(ids_pendientes),
            ),
        )

    return (
        query.filter(visibilidad)
        .order_by(Notificacion.created_at.desc())
        .all()
    )


def marcar_notificacion_como_vista(
    db: Session,
    usuario_id: uuid.UUID,
    notificacion_id: uuid.UUID,
) -> Notificacion:
    """
    Marca una notificación propia como vista para que no vuelva a mostrarse.

    Es idempotente: si ya estaba vista, retorna la misma notificación.
    """
    notificacion = (
        db.query(Notificacion)
        .filter(
            Notificacion.id == notificacion_id,
            Notificacion.usuario_id == usuario_id,
        )
        .first()
    )

    if notificacion is None:
        raise NotificacionNoEncontradaError()

    if notificacion.vista_at is None:
        notificacion.vista_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notificacion)

    return notificacion
