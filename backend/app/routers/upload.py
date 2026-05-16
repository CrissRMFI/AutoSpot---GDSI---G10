"""
Controlador HTTP — Subida de archivos.

Endpoints:
    POST /upload/foto-vehiculo

Responsabilidades:
    1. Recibir el archivo y el lado del vehículo vía multipart/form-data.
    2. Validar formato y tamaño en la capa de servicio.
    3. Delegar la subida a Cloudinary al servicio correspondiente.
    4. Devolver la URL pública y los metadatos necesarios para el payload
       de registro de vehículo.

Seguridad:
    - Requiere autenticación JWT.
    - Las credenciales de Cloudinary se leen del entorno del servidor;
      nunca se exponen al cliente.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.dependencies.auth import get_usuario_actual
from app.services.upload import subir_foto_vehiculo

LADOS_VALIDOS = {"FRENTE", "TRASERA", "LATERAL_IZQUIERDO", "LATERAL_DERECHO"}


router = APIRouter(tags=["upload"])


class FotoSubidaResponseSchema(BaseModel):
    url: str
    formato: str
    tamanio_bytes: int


@router.post(
    "/upload/foto-vehiculo",
    response_model=FotoSubidaResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Subir foto de vehículo a Cloudinary",
    description=(
        "Recibe un archivo de imagen y el lado del vehículo, lo sube a "
        "Cloudinary y devuelve la URL pública junto con los metadatos. "
        "Requiere autenticación JWT."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Foto subida exitosamente.",
        },
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
    """
    POST /upload/foto-vehiculo?lado=FRENTE

    Flujo:
        1. Valida que el lado sea uno de los cuatro requeridos.
        2. Lee el contenido del archivo.
        3. Delega la subida al servicio de Cloudinary.
        4. Devuelve url, formato y tamanio_bytes para incluir en el payload
           de registro de vehículo.
    """
    lado_normalizado = lado.strip().upper()

    if lado_normalizado not in LADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lado inválido. Valores permitidos: {', '.join(sorted(LADOS_VALIDOS))}",
        )

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
