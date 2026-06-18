"""
Servicio de la US 17D: Métricas de reputación y satisfacción.
"""
import uuid
from typing import List

from sqlalchemy.orm import Session

from app.models.valoracion import Valoracion
from app.models.testimonio import Testimonio
from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.schemas.reputacion import MetricasReputacionSchema, ReseniaDetalleSchema


def obtener_metricas_reputacion_vehiculo(db: Session, vehiculo_id: uuid.UUID) -> MetricasReputacionSchema:
    """
    Obtiene las valoraciones de un vehículo, cruza con los testimonios si existen,
    y devuelve las métricas calculadas (promedio y detalle).
    """
    resultados = (
        db.query(Valoracion, Testimonio, DatosPersonalesUsuario)
        .outerjoin(DatosPersonalesUsuario, Valoracion.conductor_id == DatosPersonalesUsuario.usuario_id)
        .outerjoin(Testimonio, Valoracion.reserva_id == Testimonio.reserva_id)
        .filter(Valoracion.vehiculo_id == vehiculo_id)
        .order_by(Valoracion.created_at.desc())
        .all()
    )

    if not resultados:
        return MetricasReputacionSchema(
            promedio_estrellas=0.0,
            cantidad_total=0,
            resenias=[]
        )

    resenias: List[ReseniaDetalleSchema] = []
    suma_puntajes = 0

    for valoracion, testimonio, datos_personales in resultados:
        suma_puntajes += valoracion.puntaje
        comentario = testimonio.descripcion if testimonio else None
        
        conductor_nombre = (
            f"{datos_personales.nombre} {datos_personales.apellido}"
            if datos_personales
            else "Conductor"
        )

        resenias.append(
            ReseniaDetalleSchema(
                puntaje=valoracion.puntaje,
                conductor=conductor_nombre,
                comentario=comentario,
                fecha=valoracion.created_at,
            )
        )

    cantidad_total = len(resultados)
    promedio = suma_puntajes / cantidad_total

    return MetricasReputacionSchema(
        promedio_estrellas=round(promedio, 1),
        cantidad_total=cantidad_total,
        resenias=resenias,
    )
