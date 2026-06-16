"""
Router — US 10R: Historial de autos.

Endpoint administrativo para que el recepcionista consulte el historial
de autos y sus movimientos.
"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_admin
from app.schemas.historial_autos import AutoHistorialSchema
from app.services.historial_autos import obtener_historial_autos

router = APIRouter(
    prefix="/admin",
    tags=["Historial Autos"],
)


@router.get(
    "/historial-autos",
    response_model=list[AutoHistorialSchema],
    summary="Consultar historial de autos",
    description=(
        "Devuelve la lista de vehículos con sus reservas asociadas. "
        "Permite filtrar por estación, fecha y patente."
    ),
)
def listar_historial_autos(
    estacion: str | None = Query(
        default=None,
        description="Filtro opcional por nombre de estación.",
    ),
    fecha: date | None = Query(
        default=None,
        description="Filtro opcional por fecha (YYYY-MM-DD).",
    ),
    patente: str | None = Query(
        default=None,
        description="Filtro opcional por patente del vehículo.",
    ),
    _admin: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> list[AutoHistorialSchema]:
    """
    GET /admin/historial-autos

    Requiere: rol ADMIN.
    Query params opcionales: estacion, fecha, patente.
    """
    return obtener_historial_autos(
        db=db,
        estacion=estacion,
        fecha=fecha,
        patente=patente,
    )
