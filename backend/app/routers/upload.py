"""
Controlador HTTP — Subida de archivos.

Endpoints:
    POST /upload/foto-vehiculo
    POST /upload/foto-dni
    POST /upload/foto-licencia

Responsabilidades:
    1. Recibir el archivo y el lado vía multipart/form-data.
    2. Validar formato y tamaño en la capa de servicio.
    3. Delegar la subida a Cloudinary al servicio correspondiente.
    4. Devolver la URL pública y los metadatos.

Seguridad:
    - Requiere autenticación JWT.
    - Las credenciales de Cloudinary se leen del entorno del servidor;
      nunca se exponen al cliente.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.dependencies.auth import get_usuario_actual
from app.services.upload import (
    subir_foto_dni,
    subir_foto_vehiculo,
    subir_imagen,
)

LADOS_VEHICULO_VALIDOS = {
    "FRENTE",
    "TRASERA",
    "LATERAL_IZQUIERDO",
    "LATERAL_DERECHO",
    "EXTRA",
}
LADOS_DNI_VALIDOS = {"FRENTE", "DORSO"}
LADOS_LICENCIA_VALIDOS = {"FRENTE", "DORSO"}


router = APIRouter(tags=["upload"])


class FotoSubidaResponseSchema(BaseModel):
    url: str
    formato: str
    tamanio_bytes: int


def _validar_lado(lado: str, valores_validos: set[str]) -> str:
    lado_normalizado = lado.strip().upper()
    if lado_normalizado not in valores_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Lado inválido. Valores permitidos: "
                f"{', '.join(sorted(valores_validos))}"
            ),
        )
    return lado_normalizado


@router.post(
    "/upload/foto-vehiculo",
    response_model=FotoSubidaResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Subir foto de vehículo a Cloudinary",
    description=(
        "Recibe un archivo de imagen y el lado del vehículo, lo sube a "
        "Cloudinary y devuelve la URL pública junto con los metadatos. "
        "Requiere autenticación JWT. Acepta el lado EXTRA para fotos "
        "adicionales más allá de las 4 obligatorias."
    ),
    responses={
        status.HTTP_201_CREATED: {"description": "Foto subida exitosamente."},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Formato inválido, tamaño excedido o lado no reconocido.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido o expirado.",
        },
    },
)
async def subir_foto(
    lado: str,
    archivo: UploadFile,
    _usuario: dict = Depends(get_usuario_actual),
) -> FotoSubidaResponseSchema:
    """POST /upload/foto-vehiculo?lado=FRENTE|EXTRA|..."""
    lado_normalizado = _validar_lado(lado, LADOS_VEHICULO_VALIDOS)
    contenido = await archivo.read()

    try:
        resultado = subir_foto_vehiculo(
            contenido=contenido,
            nombre_archivo=archivo.filename or "foto.jpg",
            lado=lado_normalizado,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al subir la imagen. Intentá de nuevo.",
        ) from exc

    return FotoSubidaResponseSchema(**resultado)


@router.post(
    "/upload/foto-dni",
    response_model=FotoSubidaResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Subir foto del DNI a Cloudinary",
    description=(
        "Recibe un archivo de imagen y el lado del DNI (FRENTE o DORSO), "
        "lo sube a Cloudinary bajo la carpeta autospot/dni y devuelve la "
        "URL pública. Requiere autenticación JWT."
    ),
    responses={
        status.HTTP_201_CREATED: {"description": "Foto subida exitosamente."},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Formato inválido, tamaño excedido o lado no reconocido.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido o expirado.",
        },
    },
)
async def subir_foto_dni_endpoint(
    lado: str,
    archivo: UploadFile,
    _usuario: dict = Depends(get_usuario_actual),
) -> FotoSubidaResponseSchema:
    """POST /upload/foto-dni?lado=FRENTE|DORSO"""
    lado_normalizado = _validar_lado(lado, LADOS_DNI_VALIDOS)
    contenido = await archivo.read()

    try:
        resultado = subir_foto_dni(
            contenido=contenido,
            nombre_archivo=archivo.filename or "dni.jpg",
            lado=lado_normalizado,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al subir la imagen. Intentá de nuevo.",
        ) from exc

    return FotoSubidaResponseSchema(**resultado)


@router.post(
    "/upload/foto-licencia",
    response_model=FotoSubidaResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Subir foto de la licencia de conducir a Cloudinary",
    description=(
        "Recibe un archivo de imagen y el lado de la licencia (FRENTE o DORSO), "
        "lo sube a Cloudinary bajo la carpeta autospot/licencia y devuelve la "
        "URL pública. Requiere autenticación JWT."
    ),
    responses={
        status.HTTP_201_CREATED: {"description": "Foto subida exitosamente."},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Formato inválido, tamaño excedido o lado no reconocido.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido o expirado.",
        },
    },
)
async def subir_foto_licencia_endpoint(
    lado: str,
    archivo: UploadFile,
    _usuario: dict = Depends(get_usuario_actual),
) -> FotoSubidaResponseSchema:
    """POST /upload/foto-licencia?lado=FRENTE|DORSO"""
    lado_normalizado = _validar_lado(lado, LADOS_LICENCIA_VALIDOS)
    contenido = await archivo.read()

    try:
        resultado = subir_imagen(
            contenido=contenido,
            nombre_archivo=archivo.filename or "licencia.jpg",
            folder="autospot/licencia",
            tags=[lado_normalizado.lower()],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al subir la imagen. Intentá de nuevo.",
        ) from exc

    return FotoSubidaResponseSchema(**resultado)
