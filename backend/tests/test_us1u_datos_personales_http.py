"""
Tests de Integración HTTP — US 1U: PUT /usuarios/{usuario_id}/datos-personales.

Metodología: TDD
  - Primero se define el contrato HTTP esperado.
  - Luego se implementa el router hasta hacer pasar los tests.

Estrategia:
  - Se usa TestClient de FastAPI.
  - Se reemplaza la sesión real por SQLite en memoria.
  - Cada test corre con una base limpia.

Criterios de Aceptación cubiertos inicialmente:
  ┌─────┬──────────────────────────────────────────────────────────────────┐
  │ CA  │ Descripción                                                      │
  ├─────┼──────────────────────────────────────────────────────────────────┤
  │ CA1 │ Cuenta creada + carga DNI, nombre y apellido                     │
  │ CA2 │ Cuenta creada + sube foto frente y dorso del DNI                 │
  └─────┴──────────────────────────────────────────────────────────────────┘

Referencias:
  - Backlog Sprint 1 — US 1U Registro datos personales
  - docs/core_negocio/dominio_actores.md
"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401


# ── Configuración de DB en memoria para tests de integración ──────────────────
TEST_DATABASE_URL = "sqlite:///:memory:"


def _make_test_engine():
    """Crea un engine SQLite en memoria con foreign keys activadas."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _override_get_db_factory(testing_session_local):
    """
    Crea un override para la dependency get_db usando la sesión de test.
    """
    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    return override_get_db


def _registrar_usuario(client: TestClient) -> str:
    """
    Helper: registra un Usuario base usando el endpoint existente de US 5U
    y retorna su id.
    """
    response = client.post(
        "/usuarios/registro",
        json={
            "email": "datos.http@autospot.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201, (
        f"No se pudo crear usuario de prueba. "
        f"Status: {response.status_code}. Body: {response.text}"
    )

    return response.json()["id"]


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 y CA2 — Registro HTTP exitoso de datos personales y documentación
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1CA2_RegistroDatosPersonalesHTTP:
    """
    Verifica el happy path HTTP de la US 1U.
    """

    def test_registra_datos_personales_y_documentacion_devuelve_201(self):
        """
        Dado un Usuario con cuenta creada,
        cuando envía DNI, nombre, apellido y fotos del DNI,
        entonces el backend responde 201 y devuelve los datos registrados.
        """
        engine = _make_test_engine()
        Base.metadata.create_all(engine)

        TestingSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )

        app.dependency_overrides[get_db] = _override_get_db_factory(
            TestingSessionLocal
        )

        try:
            with TestClient(app) as client:
                usuario_id = _registrar_usuario(client)

                payload = {
                    "dni": "00000001",
                    "nombre": "Usuario",
                    "apellido": "Prueba",
                    "foto_dni_frente_url": "uploads/dni/00000001/frente.jpg",
                    "foto_dni_dorso_url": "uploads/dni/00000001/dorso.jpg",
                }

                response = client.put(
                    f"/usuarios/{usuario_id}/datos-personales",
                    json=payload,
                )

                assert response.status_code == 201, (
                    f"Se esperaba 201, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )

                body = response.json()

                assert body["usuario_id"] == usuario_id
                assert body["dni"] == "00000001"
                assert body["nombre"] == "Usuario"
                assert body["apellido"] == "Prueba"
                assert body["foto_dni_frente_url"] == "uploads/dni/00000001/frente.jpg"
                assert body["foto_dni_dorso_url"] == "uploads/dni/00000001/dorso.jpg"
                assert body["estado_validacion"] == "PENDIENTE_VALIDACION"
                assert "id" in body

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
