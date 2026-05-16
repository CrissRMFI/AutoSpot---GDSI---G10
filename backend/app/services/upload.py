"""
Servicio de subida de archivos — Cloudinary.

Responsabilidades:
    - Configurar el SDK de Cloudinary con credenciales del entorno.
    - Subir archivos de imagen y devolver la URL pública y metadatos.
"""
import os

import cloudinary
import cloudinary.uploader

FORMATOS_PERMITIDOS = {"jpg", "jpeg", "png", "webp"}
TAMANIO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5 MB


def _configurar_cloudinary() -> None:
    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
        secure=True,
    )


def subir_foto_vehiculo(
    contenido: bytes,
    nombre_archivo: str,
    lado: str,
) -> dict:
    """
    Sube una imagen a Cloudinary bajo la carpeta autospot/vehiculos.

    Args:
        contenido       : Bytes del archivo.
        nombre_archivo  : Nombre original (usado para inferir formato).
        lado            : Lado del vehículo (FRENTE, TRASERA, etc.).

    Returns:
        dict con 'url' (str), 'formato' (str) y 'tamanio_bytes' (int).

    Raises:
        ValueError: Si el formato no está permitido o el tamaño excede el límite.
        RuntimeError: Si Cloudinary devuelve un error inesperado.
    """
    extension = nombre_archivo.rsplit(".", 1)[-1].lower() if "." in nombre_archivo else ""

    if extension not in FORMATOS_PERMITIDOS:
        raise ValueError(f"Formato '{extension}' no permitido. Usá: jpg, jpeg, png o webp.")

    if len(contenido) > TAMANIO_MAXIMO_BYTES:
        raise ValueError("El archivo supera el tamaño máximo de 5 MB.")

    _configurar_cloudinary()

    resultado = cloudinary.uploader.upload(
        contenido,
        folder="autospot/vehiculos",
        tags=[lado.lower()],
        resource_type="image",
    )

    return {
        "url": resultado["secure_url"],
        "formato": extension,
        "tamanio_bytes": len(contenido),
    }
