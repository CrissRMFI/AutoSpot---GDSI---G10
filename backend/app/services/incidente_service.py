import uuid
from datetime import datetime, timezone
from sqlalchemy import select, cast, Date, or_, and_
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.reporte import Reporte
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.models.datos_personales_usuario import DatosPersonalesUsuario


def buscar_incidentes(
    db: Session,
    codigo_reserva: str | None = None,
    conductor: str | None = None,
    fecha: str | None = None,
    patente: str | None = None,
) -> list[dict]:
    """Busca incidentes aplicando filtros opcionales."""

    query = (
        select(Reporte)
        .options(
            joinedload(Reporte.reserva),
            joinedload(Reporte.conductor),
            joinedload(Reporte.vehiculo),
        )
    )

    # Join necessary for filtering
    if codigo_reserva:
        query = query.join(Reserva, Reporte.reserva_id == Reserva.id)
        query = query.filter(Reserva.codigo.ilike(f"%{codigo_reserva}%"))
    
    if conductor:
        query = query.join(Usuario, Reporte.conductor_id == Usuario.id)
        query = query.join(DatosPersonalesUsuario, Usuario.id == DatosPersonalesUsuario.usuario_id)
        terminos = conductor.split()
        for termino in terminos:
            query = query.filter(
                or_(
                    DatosPersonalesUsuario.nombre.ilike(f"%{termino}%"),
                    DatosPersonalesUsuario.apellido.ilike(f"%{termino}%"),
                )
            )

    if patente:
        query = query.join(Vehiculo, Reporte.vehiculo_id == Vehiculo.id)
        query = query.filter(Vehiculo.patente.ilike(f"%{patente}%"))

    if fecha:
        # Asumiendo que fecha viene en formato YYYY-MM-DD
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            query = query.filter(cast(Reporte.created_at, Date) == fecha_obj)
        except ValueError:
            pass  # Ignorar filtro si la fecha es invalida

    query = query.order_by(Reporte.created_at.desc())
    reportes = db.scalars(query).all()

    resultados = []
    for r in reportes:
        # Obtenemos los datos personales del conductor si existen
        conductor_datos = None
        if r.conductor:
            conductor_datos = db.scalar(
                select(DatosPersonalesUsuario).filter(DatosPersonalesUsuario.usuario_id == r.conductor.id)
            )
            
        resultados.append({
            "id": r.id,
            "codigo_reserva": r.reserva.codigo if r.reserva else "",
            "fecha": r.created_at,
            "estado": r.estado,
            "auto": {
                "marca": r.vehiculo.marca if r.vehiculo else "",
                "modelo": r.vehiculo.modelo if r.vehiculo else "",
                "patente": r.vehiculo.patente if r.vehiculo else None,
            },
            "conductor": {
                "nombre": conductor_datos.nombre if conductor_datos else "",
                "apellido": conductor_datos.apellido if conductor_datos else "",
            }
        })

    return resultados


def obtener_incidente_detalle(db: Session, incidente_id: uuid.UUID) -> dict | None:
    """Obtiene el detalle completo de un incidente."""
    
    reporte = db.scalar(
        select(Reporte)
        .options(
            joinedload(Reporte.reserva),
            joinedload(Reporte.conductor),
            joinedload(Reporte.vehiculo),
            joinedload(Reporte.fotos)
        )
        .filter(Reporte.id == incidente_id)
    )

    if not reporte:
        return None

    propietario_datos = None
    if reporte.vehiculo and reporte.vehiculo.propietario_id:
        propietario_datos = db.scalar(
            select(DatosPersonalesUsuario).filter(DatosPersonalesUsuario.usuario_id == reporte.vehiculo.propietario_id)
        )
        
    conductor_datos = None
    if reporte.conductor:
        conductor_datos = db.scalar(
            select(DatosPersonalesUsuario).filter(DatosPersonalesUsuario.usuario_id == reporte.conductor.id)
        )

    fotos_urls = [foto.url for foto in reporte.fotos] if reporte.fotos else []

    return {
        "id": reporte.id,
        "codigo_reserva": reporte.reserva.codigo if reporte.reserva else "",
        "fecha": reporte.created_at,
        "estado": reporte.estado,
        "descripcion": reporte.descripcion,
        "auto": {
            "marca": reporte.vehiculo.marca if reporte.vehiculo else "",
            "modelo": reporte.vehiculo.modelo if reporte.vehiculo else "",
            "patente": reporte.vehiculo.patente if reporte.vehiculo else None,
        },
        "conductor": {
            "nombre": conductor_datos.nombre if conductor_datos else "",
            "apellido": conductor_datos.apellido if conductor_datos else "",
        },
        "propietario": {
            "nombre": propietario_datos.nombre if propietario_datos else "",
            "apellido": propietario_datos.apellido if propietario_datos else "",
        },
        "fotos": fotos_urls,
    }
