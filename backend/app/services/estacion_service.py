from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.estacion import Estacion


def get_estaciones_activas(db: Session) -> List[Estacion]:
    """
    Retorna la lista de estaciones activas (activa == True).
    """
    return db.query(Estacion).filter(Estacion.activa == True).all()


def get_estacion_by_id(db: Session, estacion_id: int) -> Estacion:
    """
    Retorna una estación por su ID.
    Lanza HTTPException 404 si no existe o no está activa.
    """
    estacion = db.query(Estacion).filter(Estacion.id == estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    if not estacion.activa:
        raise HTTPException(status_code=404, detail="La estación no está activa")

    return estacion


def actualizar_imagen_estacion(
    db: Session, estacion_id: int, imagen_url: Optional[str]
) -> Estacion:
    """
    Actualiza la URL de la imagen de una estación.

    Se usa principalmente desde Postman para administrar la galería visual de cada estación.
    Permite tanto estaciones activas como inactivas (es una acción de mantenimiento).
    """
    estacion = db.query(Estacion).filter(Estacion.id == estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    estacion.imagen_url = imagen_url
    db.commit()
    db.refresh(estacion)
    return estacion
