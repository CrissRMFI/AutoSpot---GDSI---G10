"""
Configuración de la base de datos para AutoSpot.

Uso:
  - Producción: PostgreSQL (variable de entorno DATABASE_URL)
  - Tests:      SQLite en memoria (inyectado por conftest.py)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://autospot_user:autospot_pass@localhost:5432/autospot_db",
)

engine = create_engine(DATABASE_URL)

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
