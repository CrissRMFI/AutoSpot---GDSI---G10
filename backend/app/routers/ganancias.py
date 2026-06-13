"""
Controlador HTTP — Dashboards de ganancias para propietarios.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    requerir_rol_propietario,
    validar_usuario_autenticado_coincide_con_id,
)
from app.exceptions import VehiculoNoEncontradoError
from app.schemas.ganancias import (
    GananciasGeneralesResponseSchema,
    GananciasVehiculoResponseSchema,
    PeriodoGanancias,
)
from app.services.ganancias import (
    obtener_ganancias_generales_propietario,
    obtener_ganancias_vehiculo_propietario,
)


router = APIRouter(tags=["Ganancias"])


@router.get(
    "/usuarios/{propietario_id}/ganancias-generales",
    response_model=GananciasGeneralesResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener dashboard de ganancias generales del propietario",
)
def obtener_ganancias_generales(
    propietario_id: uuid.UUID,
    periodo: PeriodoGanancias = Query("este_mes"),
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> GananciasGeneralesResponseSchema:
    """
    US 15D — Devuelve ingreso bruto, comisión de plataforma, ganancia neta y
    variación porcentual para el propietario autenticado.
    """
    validar_usuario_autenticado_coincide_con_id(
        usuario_id=propietario_id,
        usuario_actual=usuario_actual,
    )

    return obtener_ganancias_generales_propietario(
        db=db,
        propietario_id=propietario_id,
        periodo=periodo,
    )


@router.get(
    "/vehiculos/{vehiculo_id}/ganancias",
    response_model=GananciasVehiculoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener dashboard de ganancias de un vehículo",
)
def obtener_ganancias_vehiculo(
    vehiculo_id: uuid.UUID,
    periodo: PeriodoGanancias = Query("este_mes"),
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> GananciasVehiculoResponseSchema:
    """
    US 16D — Devuelve ingreso bruto, comisión, ganancia neta y ocupación
    para una unidad del propietario autenticado.
    """
    propietario_id = uuid.UUID(str(usuario_actual.get("sub")))

    try:
        return obtener_ganancias_vehiculo_propietario(
            db=db,
            propietario_id=propietario_id,
            vehiculo_id=vehiculo_id,
            periodo=periodo,
        )
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
