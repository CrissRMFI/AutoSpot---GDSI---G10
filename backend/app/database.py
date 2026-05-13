"""
Configuración de la base de datos para AutoSpot.

Driver: psycopg2-binary (síncrono) con SQLAlchemy 2.0.

Configuración:
  - Las credenciales se leen de variables de entorno definidas en `.env`.
  - `python-dotenv` carga el `.env` automáticamente al importar este módulo.
  - `pool_pre_ping=True` habilita reconexión automática si PostgreSQL
    cierra conexiones inactivas.

Uso:
  - Desarrollo local:  DB_HOST=localhost (con `docker compose up db -d`)
  - Docker Compose:    DB_HOST=db (inyectado por docker-compose.yml)
  - Tests:             Se sobreescribe con `app.dependency_overrides` en conftest.py.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ── Cargar variables de entorno desde .env ───────────────────────────────────
# Busca el .env en la raíz del proyecto (un nivel arriba de backend/)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# ── Construcción dinámica de DATABASE_URL ────────────────────────────────────
DB_USER: str = os.getenv("DB_USER", "autospot_user")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "autospot_pass")
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: str = os.getenv("DB_PORT", "5432")
DB_NAME: str = os.getenv("DB_NAME", "autospot_db")

DATABASE_URL: str = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Reconexión automática ante conexiones cerradas
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base declarativa compartida por todos los modelos ORM."""
    pass


def get_db():
    """
    Dependency de FastAPI que provee una sesión de DB por request.
    Garantiza cierre de la sesión aun si ocurre una excepción.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
