"""
conftest.py — Fixtures compartidas para la suite de tests de AutoSpot.

Estrategia de base de datos en tests:
  - Se usa SQLite en memoria (sqlite:///:memory:) para aislar completamente
    los tests sin requerir infraestructura de PostgreSQL.
  - Cada test recibe una sesión limpia (scope="function") y la DB se destruye
    al finalizar, garantizando idempotencia total.

Nota sobre compatibilidad SQLite/PostgreSQL:
  - El modelo usa tipos agnósticos de SQLAlchemy 2.0 (Mapped[uuid.UUID] se
    serializa como VARCHAR en SQLite y como UUID nativo en PostgreSQL).
  - Los PRAGMA de SQLite activan las foreign keys para respetar integridad.
"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture que provee una sesión de DB limpia y aislada por cada test.

    Ciclo de vida:
      1. Crea engine SQLite en memoria.
      2. Crea todas las tablas definidas en los modelos (Base.metadata).
      3. Abre una sesión y la cede al test (yield).
      4. Cierra la sesión y elimina todas las tablas (teardown automático).
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    # Activa foreign keys en SQLite (desactivadas por defecto)
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()
