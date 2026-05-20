"""
Tests HTTP — POST /upload/foto-documento-vehiculo

Cubrimos los caminos que NO disparan la llamada real a Cloudinary:
    - 401 sin token
    - 400 con tipo inválido (CEDULA, POLIZA o VTV solamente)
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from tests.conftest import _make_test_engine

from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
from app.models.foto_vehiculo import FotoVehiculo  # noqa: F401
from app.models.token_blacklist import TokenBlacklist  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401
from app.models.vehiculo import Vehiculo  # noqa: F401


def _override_get_db_factory(testing_session_local):
    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    return override_get_db


def _crear_cliente():
    engine = _make_test_engine()
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    app.dependency_overrides[get_db] = _override_get_db_factory(TestingSessionLocal)
    return engine, TestClient(app)


def _registrar_y_loguear_usuario(client, email):
    response = client.post(
        "/usuarios/registro",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 201, response.text
    usuario_id = response.json()["id"]

    response = client.post(
        "/usuarios/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return usuario_id, response.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


class TestUploadDocumentoVehiculoHTTP:
    def test_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                response = client.post(
                    "/upload/foto-documento-vehiculo?tipo=CEDULA",
                    files={"archivo": ("cedula.jpg", b"x", "image/jpeg")},
                )
                assert response.status_code == 401, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_tipo_invalido_devuelve_400(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client,
                    "owner.docveh.400@autospot.com",
                )

                response = client.post(
                    "/upload/foto-documento-vehiculo?tipo=PATENTE",
                    headers=_auth_headers(token),
                    files={"archivo": ("doc.jpg", b"x", "image/jpeg")},
                )
                assert response.status_code == 400, response.text
                assert "Tipo inválido" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_tipo_vacio_devuelve_400(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client,
                    "owner.docveh.empty@autospot.com",
                )

                response = client.post(
                    "/upload/foto-documento-vehiculo?tipo=",
                    headers=_auth_headers(token),
                    files={"archivo": ("doc.jpg", b"x", "image/jpeg")},
                )
                assert response.status_code == 400, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
