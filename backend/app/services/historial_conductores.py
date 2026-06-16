"""
Servicio — US 11R: Historial de conductores.

Lógica de negocio para consultar el historial de conductores (alquileres/reservas)
utilizado por el recepcionista desde el panel administrativo.
"""
import uuid

from sqlalchemy.orm import Session, joinedload

from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.historial_conductores import (
    AlquilerResumenSchema,
    ConductorHistorialSchema,
)


def obtener_historial_conductores(
    db: Session,
    usuario_id: uuid.UUID | None = None,
) -> list[ConductorHistorialSchema]:
    """
    Devuelve la lista de conductores que tienen al menos un alquiler,
    con sus reservas asociadas.

    Args:
        db: Sesión activa de SQLAlchemy.
        usuario_id: Si se provee, filtra los resultados a ese conductor.

    Returns:
        Lista de ConductorHistorialSchema. Vacía si no hay coincidencias.
    """
    # ── Construir query base de reservas ─────────────────────────────────────
    query = (
        db.query(Reserva)
        .join(Usuario, Reserva.conductor_id == Usuario.id)
        .outerjoin(
            DatosPersonalesUsuario,
            DatosPersonalesUsuario.usuario_id == Usuario.id,
        )
        .outerjoin(Vehiculo, Reserva.vehiculo_id == Vehiculo.id)
    )

    # ── Filtro por conductor específico ──────────────────────────────────────
    if usuario_id is not None:
        query = query.filter(Reserva.conductor_id == usuario_id)

    reservas = query.order_by(Reserva.created_at.desc()).all()

    # ── Agrupar reservas por conductor ───────────────────────────────────────
    conductores_map: dict[uuid.UUID, dict] = {}

    for reserva in reservas:
        cid = reserva.conductor_id

        if cid not in conductores_map:
            # Obtener datos personales del conductor
            datos = (
                db.query(DatosPersonalesUsuario)
                .filter(DatosPersonalesUsuario.usuario_id == cid)
                .first()
            )
            conductor_obj = (
                db.query(Usuario).filter(Usuario.id == cid).first()
            )

            conductores_map[cid] = {
                "id": cid,
                "email": conductor_obj.email if conductor_obj else "",
                "nombre": datos.nombre if datos else None,
                "apellido": datos.apellido if datos else None,
                "dni": datos.dni if datos else None,
                "alquileres": [],
            }

        # Obtener datos del vehículo asociado
        vehiculo = (
            db.query(Vehiculo)
            .filter(Vehiculo.id == reserva.vehiculo_id)
            .first()
        )

        conductores_map[cid]["alquileres"].append(
            AlquilerResumenSchema(
                id=reserva.id,
                vehiculo_id=reserva.vehiculo_id,
                estado=reserva.estado,
                fecha_inicio=reserva.fecha_inicio,
                fecha_fin=reserva.fecha_fin,
                estacion_retiro=reserva.estacion_retiro,
                monto_total=reserva.monto_total,
                vehiculo_marca=vehiculo.marca if vehiculo else None,
                vehiculo_modelo=vehiculo.modelo if vehiculo else None,
                vehiculo_patente=vehiculo.patente if vehiculo else None,
                created_at=reserva.created_at,
            )
        )

    # ── Convertir a lista de schemas ─────────────────────────────────────────
    return [
        ConductorHistorialSchema(**data)
        for data in conductores_map.values()
    ]
