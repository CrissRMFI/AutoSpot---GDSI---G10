from typing import List

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
    
    # Podríamos retornar incluso si no está activa, pero según los criterios 
    # de aceptación, normalmente el detalle es para las activas. 
    # Dejémoslo genérico o restringimos:
    if not estacion.activa:
        raise HTTPException(status_code=404, detail="La estación no está activa")

    return estacion
