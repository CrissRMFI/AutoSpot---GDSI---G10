"""
Router — US 11R: Historial de conductores.

Endpoint administrativo para que el recepcionista consulte el historial
de conductores y sus alquileres asociados.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_admin
from app.schemas.historial_conductores import ConductorHistorialSchema
from app.services.historial_conductores import obtener_historial_conductores

router = APIRouter(
    prefix="/admin",
    tags=["Historial Conductores"],
)


@router.get(
    "/historial-conductores",
    response_model=list[ConductorHistorialSchema],
    summary="Consultar historial de conductores",
    description=(
        "Devuelve la lista de conductores con sus alquileres asociados. "
        "Opcionalmente filtra por `usuario_id` para ver un conductor específico."
    ),
)
def listar_historial_conductores(
    usuario_id: uuid.UUID | None = Query(
        default=None,
        description="UUID del conductor para filtrar sus alquileres.",
    ),
    _admin: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> list[ConductorHistorialSchema]:
    """
    GET /admin/historial-conductores

    Requiere: rol ADMIN.
    Query params opcionales: usuario_id.
    """
    return obtener_historial_conductores(db=db, usuario_id=usuario_id)
