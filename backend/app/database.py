"""
Configuración de la base de datos para AutoSpot.

Driver: psycopg2-binary con SQLAlchemy 2.0.

Configuración:
  - En producción se prioriza DATABASE_URL.
  - En desarrollo local se construye la URL con DB_USER, DB_PASSWORD,
    DB_HOST, DB_PORT y DB_NAME.
  - pool_pre_ping=True habilita reconexión automática si PostgreSQL
    cierra conexiones inactivas.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ── Cargar variables de entorno desde .env ───────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


def construir_database_url() -> str:
    """
    Construye la URL de conexión a PostgreSQL.

    Prioridad:
      1. DATABASE_URL, usada normalmente en deploy.
      2. Variables separadas, usadas en desarrollo local o Docker Compose.
    """
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Algunos proveedores entregan postgres:// y SQLAlchemy espera postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        return database_url

    db_user: str = os.getenv("DB_USER", "autospot_user")
    db_password: str = os.getenv("DB_PASSWORD", "autospot_pass")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_name: str = os.getenv("DB_NAME", "autospot_db")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


DATABASE_URL = construir_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
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
        