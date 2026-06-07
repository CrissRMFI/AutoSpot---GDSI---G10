"""
Controlador HTTP — US 18C: Testimonio descriptivo de la experiencia.

Endpoints:
    POST /testimonios
        Registra un testimonio (descripción opcional) para una reserva
        finalizada. Requiere rol CLIENTE (conductor autenticado).

    GET /vehiculos/{vehiculo_id}/testimonios
        Consulta el histórico público de testimonios de un vehículo.
        Endpoint público: no requiere autenticación (CA 2).
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_cliente
from app.exceptions import (
    ReservaNoEncontradaError,
    ReservaNoFinalizadaParaTestimonioError,
    TestimonioYaRegistradoError,
)
from app.schemas.testimonio import (
    TestimonioCreatePayloadSchema,
    TestimonioResponseSchema,
)
from app.services.testimonio_service import (
    crear_testimonio,
    obtener_testimonios_por_vehiculo,
)


router = APIRouter(tags=["Testimonios"])


@router.post(
    "/testimonios",
    response_model=TestimonioResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar testimonio descriptivo de la experiencia (US 18C)",
)
def crear_testimonio_endpoint(
    payload: TestimonioCreatePayloadSchema,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(requerir_rol_cliente),
) -> TestimonioResponseSchema:
    """
    US 18C — El conductor registra un relato descriptivo sobre un alquiler
    finalizado administrativamente.

    - El campo `descripcion` es **opcional**: puede omitirse o enviarse null.
    - El testimonio se vincula de forma **permanente** al viaje y al vehículo.
    - Solo se permite **un testimonio por reserva** (inmutabilidad, CA 3).
    """
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))

    try:
        testimonio = crear_testimonio(
            db=db,
            reserva_id=payload.reserva_id,
            conductor_id=conductor_id,
            descripcion=payload.descripcion,
        )
    except ReservaNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ReservaNoFinalizadaParaTestimonioError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except TestimonioYaRegistradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return testimonio


@router.get(
    "/vehiculos/{vehiculo_id}/testimonios",
    response_model=list[TestimonioResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Consultar histórico público de testimonios de un vehículo (US 18C)",
)
def listar_testimonios_vehiculo_endpoint(
    vehiculo_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[TestimonioResponseSchema]:
    """
    US 18C — Devuelve el histórico de testimonios descriptivos de un vehículo.

    - **Endpoint público**: no requiere autenticación.
    - Permite que futuros conductores consulten la información de confianza (CA 2).
    - Devuelve lista vacía `[]` si el vehículo no tiene testimonios registrados.
    - Ordenado del más reciente al más antiguo.
    """
    return obtener_testimonios_por_vehiculo(db=db, vehiculo_id=vehiculo_id)
