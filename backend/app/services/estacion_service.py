from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.estacion import Estacion
from app.schemas.estacion import EstacionCreateRequest


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


def poblar_coordenadas_default(db: Session) -> dict:
    """
    Asigna las coordenadas por defecto a las 10 estaciones predefinidas (Spots).
    """
    coordenadas_default = [
        {"nombre": "Spot Palermo", "lat": -34.5835882, "lng": -58.4185817},
        {"nombre": "Spot Recoleta", "lat": -34.5892027, "lng": -58.3927602},
        {"nombre": "Spot Madero Premium", "lat": -34.6066985, "lng": -58.3633405},
        {"nombre": "Spot San Telmo", "lat": -34.6201864, "lng": -58.3719094},
        {"nombre": "Spot Belgrano Norte", "lat": -34.5521443, "lng": -58.4512884},
        {"nombre": "Spot Colegiales", "lat": -34.5745989, "lng": -58.4478551},
        {"nombre": "Spot Chacarita", "lat": -34.586861, "lng": -58.4533802},
        {"nombre": "Spot Villa Crespo", "lat": -34.594936, "lng": -58.4459952},
        {"nombre": "Spot Caballito Centro", "lat": -34.6029312, "lng": -58.4335271},
        {"nombre": "Spot Almagro", "lat": -34.6024284, "lng": -58.4206238},
    ]

    actualizadas = 0
    for data in coordenadas_default:
        estacion = db.query(Estacion).filter(Estacion.nombre == data["nombre"]).first()
        if estacion:
            estacion.latitud = data["lat"]
            estacion.longitud = data["lng"]
            actualizadas += 1

    db.commit()
    return {
        "detail": f"Coordenadas pobladas exitosamente. Se actualizaron {actualizadas} estaciones."
    }


def crear_estacion_manual(db: Session, data: EstacionCreateRequest) -> Estacion:
    """
    Crea una nueva estación (Spot) a discreción con latitud, longitud, nombre y descripción.
    """
    nueva_estacion = Estacion(
        nombre=data.nombre,
        direccion="A confirmar", # Dato obligatorio en BD, rellenado con un default temporal
        zona="Nueva",            # Dato obligatorio en BD, rellenado con un default temporal
        instrucciones_acceso=data.descripcion,
        latitud=data.latitud,
        longitud=data.longitud,
        activa=True
    )
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return nueva_estacion
