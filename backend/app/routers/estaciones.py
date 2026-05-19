from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.estacion import EstacionDetailResponse, EstacionListResponse
from app.services import estacion_service

router = APIRouter(
    prefix="/estaciones",
    tags=["Estaciones"],
    responses={404: {"description": "No encontrado"}},
)


@router.get("/", response_model=List[EstacionListResponse])
def listar_estaciones_activas(db: Session = Depends(get_db)):
    """
    Retorna una lista JSON que incluye únicamente las estaciones activas (activa == True).
    """
    return estacion_service.get_estaciones_activas(db)


@router.get("/{estacion_id}", response_model=EstacionDetailResponse)
def obtener_detalle_estacion(estacion_id: int, db: Session = Depends(get_db)):
    """
    Suministra la dirección exacta y las instrucciones de acceso 
    para la operatividad del retiro en una estación específica.
    """
    return estacion_service.get_estacion_by_id(db, estacion_id=estacion_id)
