"""
Controlador HTTP — Catálogo de marcas y modelos.

Endpoints:
    GET   /marcas                          → público, consumido por el frontend.
    POST  /marcas                          → ADMIN, alta de marca (Postman/Insomnia).
    POST  /marcas/{marca_id}/modelos       → ADMIN, alta de modelo (Postman/Insomnia).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_admin
from app.exceptions import (
    MarcaNoEncontradaError,
    MarcaYaExistenteError,
    ModeloYaExistenteError,
)
from app.schemas.marca import (
    MarcaCreateRequest,
    MarcaResponse,
    ModeloConMarcaResponse,
    ModeloCreateRequest,
)
from app.services import marca_service


router = APIRouter(prefix="/marcas", tags=["Marcas"])


@router.get(
    "",
    response_model=list[MarcaResponse],
    summary="Listar catálogo de marcas y modelos",
    description="Devuelve todas las marcas con sus modelos anidados.",
)
def listar_marcas(db: Session = Depends(get_db)) -> list[MarcaResponse]:
    marcas = marca_service.listar_marcas(db)
    return [MarcaResponse.model_validate(m) for m in marcas]


@router.post(
    "",
    response_model=MarcaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una marca",
    description="Alta de una marca. Reservado al rol ADMIN.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token ausente o inválido."},
        status.HTTP_403_FORBIDDEN: {"description": "Usuario sin rol ADMIN."},
        status.HTTP_409_CONFLICT: {"description": "La marca ya existe."},
    },
)
def crear_marca_endpoint(
    payload: MarcaCreateRequest,
    db: Session = Depends(get_db),
    _admin: dict = Depends(requerir_rol_admin),
) -> MarcaResponse:
    try:
        marca = marca_service.crear_marca(db, nombre=payload.nombre)
    except MarcaYaExistenteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return MarcaResponse.model_validate(marca)


@router.post(
    "/{marca_id}/modelos",
    response_model=ModeloConMarcaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un modelo bajo una marca",
    description="Alta de un modelo asociado a una marca existente. Reservado al rol ADMIN.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token ausente o inválido."},
        status.HTTP_403_FORBIDDEN: {"description": "Usuario sin rol ADMIN."},
        status.HTTP_404_NOT_FOUND: {"description": "Marca no encontrada."},
        status.HTTP_409_CONFLICT: {"description": "El modelo ya existe para esa marca."},
    },
)
def crear_modelo_endpoint(
    marca_id: int,
    payload: ModeloCreateRequest,
    db: Session = Depends(get_db),
    _admin: dict = Depends(requerir_rol_admin),
) -> ModeloConMarcaResponse:
    try:
        modelo = marca_service.crear_modelo(db, marca_id=marca_id, nombre=payload.nombre)
    except MarcaNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ModeloYaExistenteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return ModeloConMarcaResponse.model_validate(modelo)
