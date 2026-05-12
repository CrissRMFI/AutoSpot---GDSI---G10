"""
Punto de entrada de la aplicación FastAPI — AutoSpot Backend.

Responsabilidades:
    - Instanciar la aplicación FastAPI con metadatos del proyecto.
    - Registrar todos los routers de la aplicación.
    - Exponer el objeto `app` para ser levantado por Uvicorn.

Cómo ejecutar en desarrollo:
    cd backend/
    uvicorn app.main:app --reload

Documentación interactiva (generada automáticamente por FastAPI):
    - Swagger UI : http://localhost:8000/docs
    - ReDoc      : http://localhost:8000/redoc
"""
from fastapi import FastAPI

from app.routers import datos_personales_usuario as router_datos_personales
from app.routers import usuarios as router_usuarios
from app.routers import vehiculos as router_vehiculos

app = FastAPI(
    title="AutoSpot API",
    description=(
        "Backend de la plataforma AutoSpot: intermediación de alquiler de "
        "Activos (Vehículos) a través de una red de Estaciones físicas."
    ),
    version="0.1.0",
)

# ── Registro de routers ───────────────────────────────────────────────────────
app.include_router(router_usuarios.router)
app.include_router(router_vehiculos.router)
app.include_router(router_datos_personales.router)
