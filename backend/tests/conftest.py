"""
conftest.py — Fixtures compartidas para la suite de tests de AutoSpot.

Estrategia de base de datos en tests:
  - Se usa PostgreSQL (misma tecnología que producción) conectándose a la
    base `autospot_test_db` creada por `docker/init-test-db.sql`.
  - Cada test recibe tablas limpias (create_all/drop_all por función),
    garantizando idempotencia total y paridad con el entorno real.

Requisito previo:
  - El contenedor de PostgreSQL debe estar corriendo:
      docker compose up db -d

Fixtures exportadas:
  - db_session : Sesión SQLAlchemy limpia (para tests unitarios de servicios).
  - client     : TestClient de FastAPI con dependency override (para tests HTTP).

Nota sobre imports de modelos:
  - Se importan TODOS los modelos para que Base.metadata conozca todas las
    tablas al ejecutar create_all(). Sin estos imports, las tablas con foreign
    keys fallarían silenciosamente.
"""
import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.main import app

# ── Importar todos los modelos para Base.metadata ────────────────────────────
from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
from app.models.documentacion_habilitante_conductor import (  # noqa: F401
    DocumentacionHabilitanteConductor,
)
from app.models.estacion import Estacion  # noqa: F401
from app.models.foto_vehiculo import FotoVehiculo  # noqa: F401
from app.models.checkin_vehiculo import CheckinVehiculo  # noqa: F401
from app.models.checkout_vehiculo import CheckoutVehiculo  # noqa: F401
from app.models.marca import Marca, Modelo  # noqa: F401
from app.models.notificacion import Notificacion  # noqa: F401
from app.models.push_subscription import PushSubscription  # noqa: F401
from app.models.reserva import Reserva  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401
from app.models.vehiculo import Vehiculo  # noqa: F401
from app.models.token_blacklist import TokenBlacklist  # noqa: F401
from app.models.valoracion import Valoracion  # noqa: F401
from app.models.testimonio import Testimonio  # noqa: F401


# ── Catálogo inicial sembrado en cada test ───────────────────────────────────
# Reemplaza al diccionario hardcodeado que vivía en app/schemas/vehiculo.py.
# Se siembra automáticamente en las fixtures `db_session` y `client` para que
# la validación de combinación marca/modelo (delegada al servicio) tenga datos
# contra los cuales chequear.
SEED_CATALOGO_TESTS = {
    "Toyota": ["Corolla", "Etios", "Hilux"],
    "Ford": ["Fiesta", "Focus", "Ranger"],
    "Volkswagen": ["Gol", "Polo", "Amarok"],
    "Chevrolet": ["Onix", "Cruze", "S10"],
    "Renault": ["Clio", "Sandero", "Kangoo"],
}


def sembrar_catalogo(session) -> None:
    """
    Inserta marcas y modelos del catálogo inicial en una sesión activa.

    Idempotente: si una marca ya existe (p.ej. por una fixture previa en el
    mismo test que usa `client` + `db_session` juntas), no la duplica.
    """
    for nombre_marca, modelos in SEED_CATALOGO_TESTS.items():
        if session.query(Marca).filter(Marca.nombre == nombre_marca).first():
            continue
        marca = Marca(nombre=nombre_marca)
        marca.modelos = [Modelo(nombre=nombre) for nombre in modelos]
        session.add(marca)
    session.commit()

# ── Construir URL de la base de datos de test ────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

DB_USER = os.getenv("DB_USER", "autospot_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "autospot_pass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME_TEST = os.getenv("DB_NAME_TEST", "autospot_test_db")

TEST_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME_TEST}"
)


def _reset_test_schema(engine) -> None:
    """Limpia tablas y tipos PostgreSQL residuales de corridas previas."""
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        connection.execute(text(f"GRANT ALL ON SCHEMA public TO {DB_USER}"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO public"))


def _make_test_engine():
    """
    Crea un engine PostgreSQL para tests.

    Usa NullPool a propósito: la suite comparte una sola base física
    (`autospot_test_db`) y cada test recrea el schema con
    `DROP SCHEMA public CASCADE`. Con un pool persistente (el QueuePool por
    defecto), las conexiones quedaban abiertas entre tests y, como el TestClient
    atiende los requests en otro hilo, una conexión reutilizada podía consultar
    un schema a medio reconstruir por otro engine → fallos intermitentes del
    tipo `relation "tokens_blacklist" does not exist`.

    NullPool abre una conexión nueva por checkout y la cierra al devolverla, de
    modo que ninguna conexión sobrevive al test que la creó y `engine.dispose()`
    no deja nada colgado. Esto elimina la condición de carrera entre tests.
    """
    reset_engine = create_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        pool_pre_ping=True,
    )
    try:
        _reset_test_schema(reset_engine)
    finally:
        reset_engine.dispose()

    return create_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        pool_pre_ping=True,
    )



# ── Fixture: sesión de DB para tests unitarios de servicios ──────────────────

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture que provee una sesión de DB limpia y aislada por cada test.

    Ciclo de vida:
      1. Crea engine PostgreSQL de test.
      2. Crea todas las tablas definidas en los modelos (Base.metadata).
      3. Abre una sesión y la cede al test (yield).
      4. Cierra la sesión y elimina todas las tablas (teardown automático).
    """
    engine = _make_test_engine()
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = TestingSessionLocal()
    sembrar_catalogo(session)

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


# ── Fixture: TestClient HTTP para tests de integración ───────────────────────

@pytest.fixture(scope="function")
def client():
    """
    Fixture que levanta la app FastAPI completa con PostgreSQL de test.

    Ciclo de vida:
      1. Crea engine + schema (tablas) en PostgreSQL de test.
      2. Sobreescribe la dependency `get_db` de FastAPI con la DB de test.
      3. Provee un `TestClient` listo para hacer requests HTTP.
      4. Teardown: elimina tablas, libera engine y restaura overrides.

    Scope: function (tablas limpias por cada test).
    """
    engine = _make_test_engine()
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    seed_session = TestingSessionLocal()
    try:
        sembrar_catalogo(seed_session)
    finally:
        seed_session.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()
