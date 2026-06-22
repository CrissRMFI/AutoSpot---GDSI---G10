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
from app.routers import documentacion_habilitante_conductor as router_documentacion_habilitante
from app.routers import marcas as router_marcas
from app.routers import notificaciones as router_notificaciones
from app.routers import solicitudes_documentacion as router_solicitudes_documentacion
from app.routers import upload as router_upload
from app.routers import usuarios as router_usuarios
from app.routers import vehiculos as router_vehiculos
from app.routers import estaciones as router_estaciones
from app.routers import alquiler as router_alquiler
from app.routers import checkins as router_checkins
from app.routers import checkouts as router_checkouts
from app.routers import ganancias as router_ganancias
from app.routers import valoraciones as router_valoraciones
from app.routers import testimonios as router_testimonios
from app.routers import ia as router_ia
from app.routers import historial_conductores as router_historial_conductores
from app.routers import historial_autos as router_historial_autos
from app.routers import reportes as router_reportes
from app.routers import incidentes as router_incidentes

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
app.include_router(router_documentacion_habilitante.router)
app.include_router(router_upload.router)
app.include_router(router_estaciones.router)
app.include_router(router_solicitudes_documentacion.router)
app.include_router(router_notificaciones.router)
app.include_router(router_marcas.router)
app.include_router(router_alquiler.router)
app.include_router(router_checkins.router)
app.include_router(router_checkouts.router)
app.include_router(router_ganancias.router)
app.include_router(router_valoraciones.router)
app.include_router(router_testimonios.router)
app.include_router(router_ia.router)
app.include_router(router_historial_conductores.router)
app.include_router(router_historial_autos.router)
app.include_router(router_reportes.router)
app.include_router(router_incidentes.router)
