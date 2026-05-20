"""
Servicio de subida de archivos — Cloudinary.

Responsabilidades:
    - Configurar el SDK de Cloudinary con credenciales del entorno.
    - Subir archivos de imagen y devolver la URL pública y metadatos.

Diseño:
    - `subir_imagen` es la primitiva genérica que valida formato y tamaño,
      configura Cloudinary y sube a la carpeta indicada con los tags dados.
    - `subir_foto_vehiculo` y `subir_foto_dni` son wrappers que fijan
      la carpeta y los tags por dominio para mantener compatibilidad y
      ordenar los assets en Cloudinary.
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


def subir_imagen(
    contenido: bytes,
    nombre_archivo: str,
    folder: str,
    tags: list[str] | None = None,
) -> dict:
    """
    Sube una imagen genérica a Cloudinary.

    Args:
        contenido       : Bytes del archivo.
        nombre_archivo  : Nombre original (usado para inferir formato).
        folder          : Carpeta destino en Cloudinary (ej: 'autospot/dni').
        tags            : Lista opcional de tags para etiquetar el asset.

    Returns:
        dict con 'url' (str), 'formato' (str) y 'tamanio_bytes' (int).

    Raises:
        ValueError: Si el formato no está permitido o el tamaño excede el límite.
    """
    extension = (
        nombre_archivo.rsplit(".", 1)[-1].lower()
        if "." in nombre_archivo
        else ""
    )

    if extension not in FORMATOS_PERMITIDOS:
        raise ValueError(
            f"Formato '{extension}' no permitido. Usá: jpg, jpeg, png o webp."
        )

    if len(contenido) > TAMANIO_MAXIMO_BYTES:
        raise ValueError("El archivo supera el tamaño máximo de 5 MB.")

    _configurar_cloudinary()

    resultado = cloudinary.uploader.upload(
        contenido,
        folder=folder,
        tags=tags or [],
        resource_type="image",
    )

    return {
        "url": resultado["secure_url"],
        "formato": extension,
        "tamanio_bytes": len(contenido),
    }


def subir_foto_vehiculo(
    contenido: bytes,
    nombre_archivo: str,
    lado: str,
) -> dict:
    """
    Sube una foto de vehículo a la carpeta autospot/vehiculos.
    Mantiene el contrato original previo a la generalización.
    """
    return subir_imagen(
        contenido=contenido,
        nombre_archivo=nombre_archivo,
        folder="autospot/vehiculos",
        tags=[lado.lower()],
    )


def subir_foto_dni(
    contenido: bytes,
    nombre_archivo: str,
    lado: str,
) -> dict:
    """
    Sube una foto del DNI a la carpeta autospot/dni.
    El `lado` se usa como tag (FRENTE / DORSO).
    """
    return subir_imagen(
        contenido=contenido,
        nombre_archivo=nombre_archivo,
        folder="autospot/dni",
        tags=[lado.lower()],
    )
