"""
Lógica de negocio para la gestión de checkouts de vehículos (US 8R / 22C).
"""
import uuid

from sqlalchemy.orm import Session, joinedload

from app.exceptions import (
    CheckoutNoConfirmableError,
    CheckoutNoDisponibleError,
    CheckoutNoEncontradoError,
    MotivoRechazoRequeridoError,
)
from app.models.checkout_vehiculo import CheckoutVehiculo
from app.models.reserva import Reserva
from app.schemas.checkout_vehiculo import CheckoutCreatePayloadSchema
from app.services.alquiler_service import _notificar_admins
from app.services.notificacion import (
    RECURSO_RESERVA,
    TIPO_AUTO_DEVUELTO,
    TIPO_CHECKOUT_CONFIRMADO,
    TIPO_CHECKOUT_PENDIENTE_CONFIRMACION,
    TIPO_CHECKOUT_RECHAZADO,
    cerrar_notificaciones_de_reserva_por_tipo,
    crear_notificacion_usuario,
)


def crear_checkout(
    db: Session,
    schema: CheckoutCreatePayloadSchema,
    recepcionista_id: uuid.UUID,
) -> CheckoutVehiculo:
    """
    Registra el checkout (inspección de devolución) del admin.

    Precondición: la reserva debe estar DEVUELTA por recepción administrativa.
    La fecha real de devolución se fija al registrar entrada (US 7R), no
    durante el checkout.
    Cada llamada crea un registro nuevo (historial de intentos). La reserva
    queda en CHECKOUT_PENDIENTE esperando la confirmación del conductor.
    """
    reserva = (
        db.query(Reserva)
        .filter(Reserva.id == schema.reserva_id)
        .with_for_update()
        .first()
    )
    if reserva is None:
        from app.exceptions import ReservaNoEncontradaError
        raise ReservaNoEncontradaError()

    if (reserva.estado or "").upper() != "DEVUELTO" or reserva.fecha_devolucion_real is None:
        raise CheckoutNoDisponibleError()

    nuevo_checkout = CheckoutVehiculo(
        reserva_id=reserva.id,
        recepcionista_id=recepcionista_id,
        nivel_combustible=schema.nivel_combustible,
        kilometraje_actual=schema.kilometraje_actual,
        esta_limpio=schema.esta_limpio,
        tiene_danios=schema.tiene_danios,
        descripcion_danios=schema.descripcion_danios,
        url_foto_frente=schema.url_foto_frente,
        url_foto_trasera=schema.url_foto_trasera,
        url_foto_lateral_izq=schema.url_foto_lateral_izq,
        url_foto_lateral_der=schema.url_foto_lateral_der,
        url_foto_panel=schema.url_foto_panel,
        urls_fotos_danios=schema.urls_fotos_danios,
        url_foto_extra=schema.url_foto_extra,
        notas_adicionales=schema.notas_adicionales,
        estado="PENDIENTE_CONFIRMACION",
    )
    db.add(nuevo_checkout)
    reserva.estado = "CHECKOUT_PENDIENTE"
    cerrar_notificaciones_de_reserva_por_tipo(
        db=db,
        reserva_id=reserva.id,
        tipos=[TIPO_AUTO_DEVUELTO],
    )

    crear_notificacion_usuario(
        db=db,
        usuario_id=reserva.conductor_id,
        tipo=TIPO_CHECKOUT_PENDIENTE_CONFIRMACION,
        titulo="Revisá el checkout de tu alquiler",
        mensaje=(
            f"El checkout de la reserva {reserva.codigo} está listo. "
            "Confirmá o rechazá la devolución."
        ),
        recurso_tipo=RECURSO_RESERVA,
        recurso_id=reserva.id,
    )

    db.commit()
    db.refresh(nuevo_checkout)
    return nuevo_checkout


def obtener_checkout_vigente(
    db: Session,
    reserva_id: uuid.UUID,
) -> CheckoutVehiculo | None:
    """Último checkout de la reserva (el vigente para revisión del conductor)."""
    return (
        db.query(CheckoutVehiculo)
        .filter(CheckoutVehiculo.reserva_id == reserva_id)
        .order_by(CheckoutVehiculo.created_at.desc())
        .first()
    )


def _obtener_checkout_propio(
    db: Session,
    checkout_id: uuid.UUID,
    conductor_id: uuid.UUID,
) -> CheckoutVehiculo:
    checkout = (
        db.query(CheckoutVehiculo)
        .options(joinedload(CheckoutVehiculo.reserva).joinedload(Reserva.vehiculo))
        .filter(CheckoutVehiculo.id == checkout_id)
        .first()
    )
    if checkout is None or checkout.reserva.conductor_id != conductor_id:
        raise CheckoutNoEncontradoError()
    return checkout


def confirmar_checkout(
    db: Session,
    checkout_id: uuid.UUID,
    conductor_id: uuid.UUID,
) -> CheckoutVehiculo:
    """El conductor confirma el checkout: cierra el alquiler y libera el auto."""
    checkout = _obtener_checkout_propio(db, checkout_id, conductor_id)
    if (checkout.estado or "").upper() != "PENDIENTE_CONFIRMACION":
        raise CheckoutNoConfirmableError()

    checkout.estado = "CONFIRMADO"
    reserva = checkout.reserva
    reserva.estado = "FINALIZADA"
    if reserva.vehiculo is not None:
        reserva.vehiculo.disponible = True
    cerrar_notificaciones_de_reserva_por_tipo(
        db=db,
        reserva_id=reserva.id,
        tipos=[TIPO_CHECKOUT_PENDIENTE_CONFIRMACION],
    )

    _notificar_admins(
        db=db,
        tipo=TIPO_CHECKOUT_CONFIRMADO,
        titulo="Checkout confirmado",
        mensaje=f"El conductor confirmó el checkout de la reserva {reserva.codigo}. Alquiler finalizado.",
        reserva=reserva,
    )

    db.commit()
    db.refresh(checkout)
    return checkout


def rechazar_checkout(
    db: Session,
    checkout_id: uuid.UUID,
    conductor_id: uuid.UUID,
    motivo: str,
) -> CheckoutVehiculo:
    """El conductor rechaza el checkout: vuelve a DEVUELTO para reenvío del admin."""
    motivo_limpio = (motivo or "").strip()
    if not motivo_limpio:
        raise MotivoRechazoRequeridoError()

    checkout = _obtener_checkout_propio(db, checkout_id, conductor_id)
    if (checkout.estado or "").upper() != "PENDIENTE_CONFIRMACION":
        raise CheckoutNoConfirmableError()

    checkout.estado = "RECHAZADO"
    checkout.motivo_rechazo = motivo_limpio
    reserva = checkout.reserva
    reserva.estado = "DEVUELTO"
    cerrar_notificaciones_de_reserva_por_tipo(
        db=db,
        reserva_id=reserva.id,
        tipos=[TIPO_CHECKOUT_PENDIENTE_CONFIRMACION],
    )

    _notificar_admins(
        db=db,
        tipo=TIPO_CHECKOUT_RECHAZADO,
        titulo="Checkout rechazado",
        mensaje=f"El conductor rechazó el checkout de la reserva {reserva.codigo}. Motivo: {motivo_limpio}",
        reserva=reserva,
    )

    db.commit()
    db.refresh(checkout)
    return checkout
