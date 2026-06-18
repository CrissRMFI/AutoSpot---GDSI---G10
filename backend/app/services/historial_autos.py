"""
Servicio — US 10R: Historial de autos.

Lógica de negocio para consultar el historial de movimientos de autos (reservas)
utilizado por el recepcionista desde el panel administrativo.
"""
from datetime import date
import uuid

from sqlalchemy import cast, Date
from sqlalchemy.orm import Session

from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.historial_autos import (
    MovimientoAutoSchema,
    AutoHistorialSchema,
)


def obtener_historial_autos(
    db: Session,
    estacion: str | None = None,
    fecha: date | None = None,
    patente: str | None = None,
) -> list[AutoHistorialSchema]:
    """
    Devuelve la lista de vehículos con sus reservas (movimientos) asociadas.
    Aplica filtros opcionales de estación, fecha y patente.
    """
    query = (
        db.query(Reserva)
        .join(Vehiculo, Reserva.vehiculo_id == Vehiculo.id)
        .join(Usuario, Reserva.conductor_id == Usuario.id)
        .outerjoin(
            DatosPersonalesUsuario,
            DatosPersonalesUsuario.usuario_id == Usuario.id,
        )
    )

    if estacion:
        query = query.filter(Reserva.estacion_retiro.ilike(f"%{estacion}%"))
    
    if patente:
        query = query.filter(Vehiculo.patente.ilike(f"%{patente}%"))

    if fecha:
        # Verifica si la fecha consultada cae dentro del período de la reserva
        query = query.filter(
            cast(Reserva.fecha_inicio, Date) <= fecha,
            cast(Reserva.fecha_fin, Date) >= fecha,
        )

    reservas = query.order_by(Reserva.created_at.desc()).all()

    autos_map: dict[uuid.UUID, dict] = {}

    for reserva in reservas:
        vid = reserva.vehiculo_id

        if vid not in autos_map:
            vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vid).first()
            autos_map[vid] = {
                "id": vid,
                "marca": vehiculo.marca if vehiculo else "",
                "modelo": vehiculo.modelo if vehiculo else "",
                "patente": vehiculo.patente if vehiculo else None,
                "movimientos": [],
            }

        cid = reserva.conductor_id
        conductor_obj = db.query(Usuario).filter(Usuario.id == cid).first()
        datos = (
            db.query(DatosPersonalesUsuario)
            .filter(DatosPersonalesUsuario.usuario_id == cid)
            .first()
        )

        autos_map[vid]["movimientos"].append(
            MovimientoAutoSchema(
                id=reserva.id,
                conductor_id=cid,
                conductor_email=conductor_obj.email if conductor_obj else "",
                conductor_nombre=datos.nombre if datos else None,
                conductor_apellido=datos.apellido if datos else None,
                estado=reserva.estado,
                fecha_inicio=reserva.fecha_inicio,
                fecha_fin=reserva.fecha_fin,
                estacion_retiro=reserva.estacion_retiro,
                created_at=reserva.created_at,
            )
        )

    return [
        AutoHistorialSchema(**data)
        for data in autos_map.values()
    ]
