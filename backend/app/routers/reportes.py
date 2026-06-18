"""
Endpoints HTTP — Reportes de falla critica.

Rutas:
    GET  /reportes/{reporte_id}            -> conductor, propietario o admin
    POST /reportes/{reporte_id}/resolver   -> admin o propietario del vehiculo
    GET  /admin/reportes                   -> admin
    GET  /admin/reportes/{reporte_id}      -> admin
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_usuario_actual, requerir_rol_admin
from app.exceptions import (
    ReporteNoEncontradoError,
    ReporteNoPerteneceAPropietarioError,
    ReporteNoResolubleError,
)
from app.models.reporte import Reporte
from app.schemas.reporte import (
    ReporteDetalleSchema,
    ReporteResponseSchema,
    ResolverReportePayloadSchema,
)
from app.services.reporte_service import (
    listar_reportes,
    obtener_reporte,
    resolver_reporte,
    usuario_puede_ver_reporte,
)

router = APIRouter(tags=["Reportes"])


def _a_detalle(reporte: Reporte) -> ReporteDetalleSchema:
    """Arma el detalle del reporte enriquecido con datos del vehiculo/reserva."""
    detalle = ReporteDetalleSchema.model_validate(reporte)
    vehiculo = reporte.vehiculo
    if vehiculo is not None:
        detalle.vehiculo_marca = vehiculo.marca
        detalle.vehiculo_modelo = vehiculo.modelo
        detalle.vehiculo_anio = vehiculo.anio
    if reporte.reserva is not None:
        detalle.codigo_reserva = reporte.reserva.codigo
    return detalle


@router.get(
    "/reportes/{reporte_id}",
    response_model=ReporteDetalleSchema,
    summary="Detalle de un reporte de incidencia",
)
def obtener_reporte_endpoint(
    reporte_id: uuid.UUID,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> ReporteDetalleSchema:
    try:
        reporte = obtener_reporte(db=db, reporte_id=reporte_id)
    except ReporteNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if not usuario_puede_ver_reporte(db=db, reporte=reporte, usuario_actual=usuario_actual):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para ver este reporte",
        )
    return _a_detalle(reporte)


@router.post(
    "/reportes/{reporte_id}/resolver",
    response_model=ReporteResponseSchema,
    summary="Registra la resolucion de un reporte (admin o propietario)",
)
def resolver_reporte_endpoint(
    reporte_id: uuid.UUID,
    payload: ResolverReportePayloadSchema,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> ReporteResponseSchema:
    try:
        reporte = resolver_reporte(
            db=db,
            reporte_id=reporte_id,
            usuario_actual=usuario_actual,
            schema=payload,
        )
    except ReporteNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ReporteNoPerteneceAPropietarioError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ReporteNoResolubleError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return ReporteResponseSchema.model_validate(reporte)


@router.get(
    "/admin/reportes",
    response_model=list[ReporteDetalleSchema],
    summary="Lista de reportes para administracion",
)
def listar_reportes_admin_endpoint(
    estado: str | None = Query(default=None, description="Filtra por estado (ACTIVO/RESUELTO)."),
    _admin: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> list[ReporteDetalleSchema]:
    reportes = listar_reportes(db=db, estado=estado)
    return [_a_detalle(reporte) for reporte in reportes]


@router.get(
    "/admin/reportes/{reporte_id}",
    response_model=ReporteDetalleSchema,
    summary="Detalle de un reporte para administracion",
)
def obtener_reporte_admin_endpoint(
    reporte_id: uuid.UUID,
    _admin: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> ReporteDetalleSchema:
    try:
        reporte = obtener_reporte(db=db, reporte_id=reporte_id)
    except ReporteNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _a_detalle(reporte)
