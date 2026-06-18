"""
Servicio de negocio — Reportes de falla critica durante el alquiler.

Un reporte critico se crea durante un alquiler en curso. Asocia la falla a la
reserva, conductor y vehiculo, incluye descripcion general y entre 1 y 10 fotos
con descripcion obligatoria. Al crearse, la reserva pasa a INCIDENTE_REPORTADO,
el vehiculo se mantiene fuera del catalogo y se notifica al propietario y a los
admins. La resolucion (admin o propietario del vehiculo) no reactiva la
disponibilidad del auto.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.exceptions import (
    ReporteDuplicadoError,
    ReporteFotosRequeridasError,
    ReporteNoEncontradoError,
    ReporteNoPerteneceAPropietarioError,
    ReporteNoResolubleError,
    ReservaNoEnCursoError,
    ReservaNoEncontradaError,
    VehiculoNoEncontradoError,
)
from app.models.reporte import (
    CRITICIDAD_CRITICA,
    ESTADO_ACTIVO,
    ESTADO_RESUELTO,
    TIPO_FALLA,
    Reporte,
)
from app.models.reporte_foto import ReporteFoto
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.schemas.reporte import ReportePayloadSchema, ResolverReportePayloadSchema
from app.services.notificacion import (
    crear_notificacion_reporte_falla_propietario,
    crear_notificaciones_reporte_falla_admins,
)

# Estados de reserva desde los que se admite reportar una falla critica.
ESTADOS_REPORTABLES = {"EN_CURSO"}
# Estado al que pasa la reserva tras registrar el reporte.
ESTADO_RESERVA_INCIDENTE = "INCIDENTE_REPORTADO"


def obtener_reporte(db: Session, reporte_id: uuid.UUID) -> Reporte:
    """Devuelve un reporte con sus fotos, vehiculo y reserva, o lanza 404."""
    reporte = (
        db.query(Reporte)
        .options(
            joinedload(Reporte.fotos),
            joinedload(Reporte.vehiculo),
            joinedload(Reporte.reserva),
        )
        .filter(Reporte.id == reporte_id)
        .first()
    )
    if reporte is None:
        raise ReporteNoEncontradoError()
    return reporte


def obtener_reporte_por_reserva(db: Session, reserva_id: uuid.UUID) -> Reporte | None:
    """Devuelve el reporte de una reserva si existe, o None."""
    return (
        db.query(Reporte)
        .options(joinedload(Reporte.fotos))
        .filter(Reporte.reserva_id == reserva_id)
        .first()
    )


def obtener_reporte_activo_por_vehiculo(
    db: Session, vehiculo_id: uuid.UUID
) -> Reporte | None:
    """Devuelve el reporte ACTIVO de un vehiculo si existe, o None."""
    return (
        db.query(Reporte)
        .filter(
            Reporte.vehiculo_id == vehiculo_id,
            Reporte.estado == ESTADO_ACTIVO,
        )
        .first()
    )


def listar_reportes(db: Session, estado: str | None = None) -> list[Reporte]:
    """Lista reportes (opcionalmente filtrados por estado) para la vista admin."""
    query = db.query(Reporte).options(
        joinedload(Reporte.fotos),
        joinedload(Reporte.vehiculo),
        joinedload(Reporte.reserva),
    )
    if estado:
        query = query.filter(Reporte.estado == estado.upper())
    return query.order_by(Reporte.created_at.desc()).all()


def usuario_puede_ver_reporte(
    db: Session,
    reporte: Reporte,
    usuario_actual: dict,
) -> bool:
    """
    Indica si el usuario puede ver el reporte.

    Pueden verlo el conductor de la reserva, el propietario del vehiculo y
    cualquier admin.
    """
    usuario_id = usuario_actual.get("sub")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        return False

    if (usuario.rol or "").upper() == "ADMIN":
        return True
    if reporte.conductor_id == usuario.id:
        return True
    vehiculo = reporte.vehiculo
    return vehiculo is not None and vehiculo.propietario_id == usuario.id


def crear_reporte_falla_critica(
    db: Session,
    reserva_id: uuid.UUID,
    conductor_id: uuid.UUID,
    schema: ReportePayloadSchema,
) -> Reporte:
    """
    Registra un reporte de falla critica para una reserva en curso (US 16C).

    Pasa la reserva a INCIDENTE_REPORTADO, mantiene el vehiculo fuera del
    catalogo y notifica al propietario y a los admins, todo en una transaccion.
    """
    reserva = (
        db.query(Reserva)
        .filter(Reserva.id == reserva_id)
        .with_for_update()
        .first()
    )
    if reserva is None or reserva.conductor_id != conductor_id:
        raise ReservaNoEncontradaError()

    if (reserva.estado or "").upper() not in ESTADOS_REPORTABLES:
        raise ReservaNoEnCursoError(
            "Solo se pueden reportar fallas criticas de alquileres en curso."
        )

    if reserva.vehiculo is None:
        raise VehiculoNoEncontradoError("La reserva no tiene un vehículo asociado.")

    existente = (
        db.query(Reporte).filter(Reporte.reserva_id == reserva.id).first()
    )
    if existente is not None:
        raise ReporteDuplicadoError()

    if not schema.fotos:
        raise ReporteFotosRequeridasError()

    reporte = Reporte(
        reserva_id=reserva.id,
        conductor_id=conductor_id,
        vehiculo_id=reserva.vehiculo.id,
        descripcion=schema.descripcion.strip(),
        tipo=TIPO_FALLA,
        criticidad=CRITICIDAD_CRITICA,
        estado=ESTADO_ACTIVO,
    )
    for foto in schema.fotos:
        reporte.fotos.append(
            ReporteFoto(
                url=foto.url,
                descripcion=foto.descripcion,
                formato=foto.formato,
                tamanio_bytes=foto.tamanio_bytes,
                orden=foto.orden,
            )
        )

    db.add(reporte)

    # La reserva entra en contingencia y el auto no vuelve al catalogo.
    reserva.estado = ESTADO_RESERVA_INCIDENTE
    reserva.vehiculo.disponible = False

    db.flush()  # asegura reporte.id y relaciones para las notificaciones

    crear_notificacion_reporte_falla_propietario(db=db, reporte=reporte)
    crear_notificaciones_reporte_falla_admins(db=db, reporte=reporte)

    db.commit()
    db.refresh(reporte)
    return reporte


def usuario_puede_resolver_reporte(
    db: Session,
    reporte: Reporte,
    usuario_actual: dict,
) -> bool:
    """
    Indica si el usuario puede resolver el reporte.

    ADMIN puede resolver cualquiera; PROPIETARIO solo si el vehiculo le
    pertenece; CLIENTE nunca.
    """
    usuario_id = usuario_actual.get("sub")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        return False

    rol = (usuario.rol or "").upper()
    if rol == "ADMIN":
        return True
    if rol == "PROPIETARIO":
        vehiculo = reporte.vehiculo
        return vehiculo is not None and vehiculo.propietario_id == usuario.id
    return False


def resolver_reporte(
    db: Session,
    reporte_id: uuid.UUID,
    usuario_actual: dict,
    schema: ResolverReportePayloadSchema,
) -> Reporte:
    """
    Registra la resolucion de un reporte ACTIVO.

    No reactiva la disponibilidad del vehiculo: esa decision queda en manos del
    propietario.
    """
    reporte = obtener_reporte(db=db, reporte_id=reporte_id)

    if reporte.estado != ESTADO_ACTIVO:
        raise ReporteNoResolubleError()

    if not usuario_puede_resolver_reporte(
        db=db, reporte=reporte, usuario_actual=usuario_actual
    ):
        raise ReporteNoPerteneceAPropietarioError()

    reporte.estado = ESTADO_RESUELTO
    reporte.resuelto_at = datetime.now(timezone.utc)
    reporte.resuelto_por_id = uuid.UUID(str(usuario_actual.get("sub")))
    reporte.resolucion_descripcion = schema.resolucion_descripcion.strip()

    db.commit()
    db.refresh(reporte)
    return reporte
