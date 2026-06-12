"""
Controlador HTTP — US 15D: Dashboard de ganancias generales.
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    requerir_rol_propietario,
    validar_usuario_autenticado_coincide_con_id,
)
from app.schemas.ganancias import GananciasGeneralesResponseSchema, PeriodoGanancias
from app.services.ganancias import obtener_ganancias_generales_propietario


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
