"""
Tests de Integración HTTP — US 2U: POST /usuarios/login.

Metodología: TDD (fase VERDE desde el inicio, escribiendo tests que fallan
hasta implementar el endpoint).

Criterios de Aceptación:
    CA1: Login exitoso devuelve información del usuario y otorga acceso.
    CA2: Login fallido (email o password incorrectos) devuelve el mismo error genérico.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Configuración SQLite en memoria para tests
TEST_DATABASE_URL = "sqlite:///:memory:"


def _make_test_engine():
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


@pytest.fixture()
def client():
    engine = _make_test_engine()
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

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


_ENDPOINT_LOGIN = "/usuarios/login"
_ENDPOINT_REGISTRO = "/usuarios/registro"


def _registrar_usuario_test(client: TestClient, email: str, password: str):
    return client.post(
        _ENDPOINT_REGISTRO,
        json={"email": email, "password": password},
    )


class TestCA1_LoginExitosoHTTP:
    """
    Verifica que con credenciales válidas, el usuario ingresa exitosamente.
    """

    def test_login_exitoso_devuelve_200_y_usuario(self, client: TestClient):
        # 1. Registrar usuario
        _registrar_usuario_test(client, "valido@test.com", "Password123!")

        # 2. Iniciar sesión
        response = client.post(
            _ENDPOINT_LOGIN,
            json={"email": "valido@test.com", "password": "Password123!"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["email"] == "valido@test.com"
        assert "id" in body
        assert "is_active" in body


class TestCA2_LoginFallidoHTTP:
    """
    Verifica que cualquier fallo (email no existe, clave mala)
    devuelve 401 Unauthorized y el mismo mensaje genérico para no revelar
    información de la cuenta.
    """

    def test_login_fallido_email_inexistente_devuelve_401(self, client: TestClient):
        response = client.post(
            _ENDPOINT_LOGIN,
            json={"email": "noexiste@test.com", "password": "Password123!"},
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Credenciales incorrectas"}

    def test_login_fallido_password_incorrecto_devuelve_401(self, client: TestClient):
        # 1. Registrar usuario
        _registrar_usuario_test(client, "valido2@test.com", "Password123!")

        # 2. Iniciar sesión con clave incorrecta
        response = client.post(
            _ENDPOINT_LOGIN,
            json={"email": "valido2@test.com", "password": "ClaveEquivocada!"},
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Credenciales incorrectas"}
