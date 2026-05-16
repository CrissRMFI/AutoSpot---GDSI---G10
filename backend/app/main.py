"""
Punto de entrada de la aplicación FastAPI — AutoSpot Backend.

Responsabilidades:
    - Instanciar la aplicación FastAPI con metadatos del proyecto.
    - Registrar todos los routers de la aplicación.
    - Exponer el objeto `app` para ser levantado por Uvicorn.

Cómo ejecutar en desarrollo:
    cd backend/
    uvicorn app.main:app --reload

"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import datos_personales_usuario as router_datos_personales
from app.routers import upload as router_upload
from app.routers import usuarios as router_usuarios
from app.routers import vehiculos as router_vehiculos


def obtener_origenes_cors() -> list[str]:
    """
    Obtiene los orígenes permitidos para CORS.

    En producción se usa CORS_ALLOW_ORIGINS con URLs separadas por coma.
    En desarrollo local se permiten los orígenes habituales de Vite/React.
    """
    origenes = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    )

    return [
        origen.strip()
        for origen in origenes.split(",")
        if origen.strip()
    ]


app = FastAPI(
    title="AutoSpot API",
    description=(
        "Backend de la plataforma AutoSpot: intermediación de alquiler de "
        "Activos (Vehículos) a través de una red de Estaciones físicas."
    ),
    version="0.1.0",
)

# ── Configuración CORS ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=obtener_origenes_cors(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registro de routers ───────────────────────────────────────────────────────
app.include_router(router_usuarios.router)
app.include_router(router_vehiculos.router)
app.include_router(router_datos_personales.router)
app.include_router(router_upload.router)