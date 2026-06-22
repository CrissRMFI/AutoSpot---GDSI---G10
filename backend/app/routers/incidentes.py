import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_admin
from app.schemas.incidente import IncidenteListResponseSchema, IncidenteDetalleResponseSchema
from app.services.incidente_service import buscar_incidentes, obtener_incidente_detalle


router = APIRouter(prefix="/admin/incidentes", tags=["Incidentes (Admin)"])


@router.get(
    "",
    response_model=list[IncidenteListResponseSchema],
    summary="Lista de incidentes con filtros",
)
def listar_incidentes_admin_endpoint(
    codigo_reserva: str | None = Query(default=None, description="Filtrar por codigo de reserva"),
    conductor: str | None = Query(default=None, description="Filtrar por nombre/apellido del conductor"),
    fecha: str | None = Query(default=None, description="Filtrar por fecha exacta YYYY-MM-DD"),
    patente: str | None = Query(default=None, description="Filtrar por patente del vehiculo"),
    _admin: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
):
    resultados = buscar_incidentes(
        db=db,
        codigo_reserva=codigo_reserva,
        conductor=conductor,
        fecha=fecha,
        patente=patente,
    )
    return [IncidenteListResponseSchema.model_validate(r) for r in resultados]


@router.get(
    "/{incidente_id}",
    response_model=IncidenteDetalleResponseSchema,
    summary="Detalle de un incidente para administracion",
)
def obtener_incidente_admin_endpoint(
    incidente_id: uuid.UUID,
    _admin: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
):
    detalle = obtener_incidente_detalle(db=db, incidente_id=incidente_id)
    if not detalle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
    
    return IncidenteDetalleResponseSchema.model_validate(detalle)
