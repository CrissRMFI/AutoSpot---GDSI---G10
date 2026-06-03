"""
Lógica de negocio para la gestión de check-ins de vehículos (US 15C).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.checkin_vehiculo import CheckinVehiculo
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.schemas.checkin_vehiculo import (
    CheckinCreatePayloadSchema,
    CheckinUpdatePayloadSchema,
)
from app.services.notificacion import crear_notificacion_usuario

MENSAJES_CHECKIN_EXISTENTE = {
    "PENDIENTE": "Ya enviaste el check-in de esta reserva. Esperá la revisión del administrador.",
    "APROBADO": "El check-in de esta reserva ya fue aprobado.",
    "RECHAZADO": "El check-in de esta reserva fue rechazado. Debés reenviar la corrección desde el check-in existente.",
}


def _obtener_admin_para_notificar(db: Session) -> Usuario | None:
    """
    Obtiene el administrador al que se le enviará la notificación.
    NOTA: Lo correcto sería obtener el admin que verificó el código,
    pero al no estar persistido ese dato en Reserva, se envía al 
    primer admin disponible (según indicación de que hay solo un admin).
    """
    return db.query(Usuario).filter(Usuario.rol == "ADMIN", Usuario.is_active.is_(True)).first()


def crear_checkin(
    db: Session,
    schema: CheckinCreatePayloadSchema,
    conductor_id: uuid.UUID,
) -> CheckinVehiculo:
    """
    Crea el check-in inicial y notifica al administrador.
    """
    # 1. Validar que la reserva exista, pertenezca al conductor y esté VERIFICADA
    reserva = db.query(Reserva).filter(Reserva.id == schema.reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )
    if reserva.conductor_id != conductor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La reserva no pertenece a este conductor.",
        )
    if reserva.estado != "VERIFICADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede hacer check-in de una reserva VERIFICADA.",
        )

    # 2. Verificar que no exista ya un check-in para esta reserva
    existente = db.query(CheckinVehiculo).filter(CheckinVehiculo.reserva_id == reserva.id).first()
    if existente:
        estado_existente = (existente.estado or "").upper()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=MENSAJES_CHECKIN_EXISTENTE.get(
                estado_existente,
                "El check-in para esta reserva ya fue iniciado.",
            ),
        )

    # 3. Crear el check-in
    nuevo_checkin = CheckinVehiculo(
        reserva_id=reserva.id,
        conductor_id=conductor_id,
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
        estado="PENDIENTE"
    )
    db.add(nuevo_checkin)
    db.flush()

    # 4. Notificar al Admin
    admin = _obtener_admin_para_notificar(db)
    if admin:
        crear_notificacion_usuario(
            db=db,
            usuario_id=admin.id,
            tipo="CHECKIN_PENDIENTE",
            titulo="Revisión de Check-in",
            mensaje=f"El conductor ha enviado el check-in de la reserva {reserva.codigo} para su revisión.",
            recurso_tipo="CHECKIN",
            recurso_id=nuevo_checkin.id,
        )

    db.commit()
    db.refresh(nuevo_checkin)
    return nuevo_checkin


def re_enviar_checkin(
    db: Session,
    checkin_id: uuid.UUID,
    schema: CheckinUpdatePayloadSchema,
    conductor_id: uuid.UUID,
) -> CheckinVehiculo:
    """
    Actualiza un check-in existente SOLO si estaba en estado RECHAZADO.
    """
    checkin = db.query(CheckinVehiculo).options(joinedload(CheckinVehiculo.reserva)).filter(CheckinVehiculo.id == checkin_id).first()
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in no encontrado.",
        )
    if checkin.conductor_id != conductor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para editar este check-in.",
        )
    if checkin.estado != "RECHAZADO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden editar check-ins en estado RECHAZADO.",
        )

    # Actualizar datos
    checkin.nivel_combustible = schema.nivel_combustible
    checkin.kilometraje_actual = schema.kilometraje_actual
    checkin.esta_limpio = schema.esta_limpio
    checkin.tiene_danios = schema.tiene_danios
    checkin.descripcion_danios = schema.descripcion_danios
    checkin.url_foto_frente = schema.url_foto_frente
    checkin.url_foto_trasera = schema.url_foto_trasera
    checkin.url_foto_lateral_izq = schema.url_foto_lateral_izq
    checkin.url_foto_lateral_der = schema.url_foto_lateral_der
    checkin.url_foto_panel = schema.url_foto_panel
    checkin.urls_fotos_danios = schema.urls_fotos_danios
    checkin.url_foto_extra = schema.url_foto_extra
    checkin.notas_adicionales = schema.notas_adicionales

    # Cambiar estado
    checkin.estado = "PENDIENTE"
    checkin.motivo_rechazo = None

    # Notificar de nuevo
    admin = _obtener_admin_para_notificar(db)
    if admin:
        crear_notificacion_usuario(
            db=db,
            usuario_id=admin.id,
            tipo="CHECKIN_PENDIENTE",
            titulo="Check-in Reenviado",
            mensaje=f"El conductor ha corregido y reenviado el check-in de la reserva {checkin.reserva.codigo}.",
            recurso_tipo="CHECKIN",
            recurso_id=checkin.id,
        )

    db.commit()
    db.refresh(checkin)
    return checkin


def obtener_checkin_de_reserva_conductor(
    db: Session,
    reserva_id: uuid.UUID,
    conductor_id: uuid.UUID,
) -> CheckinVehiculo | None:
    """
    Devuelve el check-in propio de una reserva, si existe.

    Permite al conductor saber si debe esperar revisión, puede corregir un
    rechazo o ya tiene el check-in aprobado.
    """
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )
    if reserva.conductor_id != conductor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La reserva no pertenece a este conductor.",
        )

    return (
        db.query(CheckinVehiculo)
        .filter(CheckinVehiculo.reserva_id == reserva_id)
        .first()
    )


def listar_checkins_pendientes(db: Session):
    return (
        db.query(CheckinVehiculo)
        .options(joinedload(CheckinVehiculo.reserva))
        .filter(CheckinVehiculo.estado == "PENDIENTE")
        .order_by(CheckinVehiculo.created_at.asc())
        .all()
    )


def listar_checkins(db: Session):
    """Todos los check-ins, con los PENDIENTE primero y luego por fecha desc."""
    return (
        db.query(CheckinVehiculo)
        .options(joinedload(CheckinVehiculo.reserva))
        .order_by(
            (CheckinVehiculo.estado != "PENDIENTE"),
            CheckinVehiculo.created_at.desc(),
        )
        .all()
    )


def obtener_checkin(db: Session, checkin_id: uuid.UUID) -> CheckinVehiculo | None:
    """Obtiene un check-in por id, en cualquier estado (para la vista de detalle)."""
    return (
        db.query(CheckinVehiculo)
        .options(joinedload(CheckinVehiculo.reserva))
        .filter(CheckinVehiculo.id == checkin_id)
        .first()
    )


def aprobar_checkin(db: Session, checkin_id: uuid.UUID) -> CheckinVehiculo:
    checkin = db.query(CheckinVehiculo).filter(CheckinVehiculo.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in no encontrado")
    
    checkin.estado = "APROBADO"
    
    crear_notificacion_usuario(
        db=db,
        usuario_id=checkin.conductor_id,
        tipo="CHECKIN_APROBADO",
        titulo="Check-in Aprobado",
        mensaje=f"Tu check-in ha sido aprobado. Puedes iniciar el alquiler.",
        recurso_tipo="RESERVA",
        recurso_id=checkin.reserva_id,
    )
    
    db.commit()
    db.refresh(checkin)
    return checkin


def rechazar_checkin(db: Session, checkin_id: uuid.UUID, motivo: str) -> CheckinVehiculo:
    if not motivo or not motivo.strip():
        raise HTTPException(status_code=400, detail="Motivo de rechazo obligatorio")
        
    checkin = db.query(CheckinVehiculo).filter(CheckinVehiculo.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in no encontrado")
        
    checkin.estado = "RECHAZADO"
    checkin.motivo_rechazo = motivo
    
    crear_notificacion_usuario(
        db=db,
        usuario_id=checkin.conductor_id,
        tipo="CHECKIN_RECHAZADO",
        titulo="Check-in Rechazado",
        mensaje=f"Tu check-in ha sido rechazado. Motivo: {motivo}",
        recurso_tipo="RESERVA",
        recurso_id=checkin.reserva_id,
    )
    
    db.commit()
    db.refresh(checkin)
    return checkin
