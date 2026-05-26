"""
Endpoints HTTP para la gestión de alquileres.
"""
from fastapi import APIRouter, HTTPException, status

from app.schemas.alquiler import SimularTiempoAlquilerRequest, SimularTiempoAlquilerResponse
from app.services.alquiler_service import calcular_tiempo_alquiler

router = APIRouter(
    prefix="/alquiler",
    tags=["Alquiler"]
)


@router.post(
    "/simular-tiempo",
    response_model=SimularTiempoAlquilerResponse,
    status_code=status.HTTP_200_OK,
    summary="Simular y validar tiempo de alquiler",
)
def simular_tiempo(payload: SimularTiempoAlquilerRequest):
    """
    Verifica que el periodo definido entre la fecha de inicio y fin sea válido
    (mínimo 1 día) y calcula la duración total exacta en días y horas.
    """
    try:
        resultado = calcular_tiempo_alquiler(payload.fecha_inicio, payload.fecha_fin)
        return SimularTiempoAlquilerResponse(**resultado)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
