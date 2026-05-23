"""
Tests de Integración HTTP — US 1C: documentación habilitante del Conductor.

Endpoints bajo prueba:
    GET /usuarios/{usuario_id}/documentacion-habilitante
    PUT /usuarios/{usuario_id}/documentacion-habilitante
    PUT /usuarios/{usuario_id}/documentacion-habilitante/actualizar

Contrato HTTP esperado:
    201 → registro exitoso
    200 → consulta o actualización exitosa
    401 → token ausente
    403 → recurso ajeno
    404 → recurso inexistente
    409 → documentación ya registrada
    422 → payload inválido
"""
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from tests.conftest import _make_test_engine

from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
from app.models.documentacion_habilitante_conductor import (  # noqa: F401
    DocumentacionHabilitanteConductor,
)
from app.models.token_blacklist import TokenBlacklist  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401


PAYLOAD_VALIDO = {
    "numero_licencia": "LIC-12345678",
    "categoria": "B",
    "fecha_emision": "2024-01-10",
    "fecha_vencimiento": "2029-01-10",
    "foto_licencia_frente_url": "uploads/licencia/12345678/frente.jpg",
    "foto_licencia_dorso_url": "uploads/licencia/12345678/dorso.jpg",
}


def _override_get_db_factory(testing_session_local):
    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    return override_get_db


def _registrar_usuario(
    client: TestClient,
    email: str = "conductor.http@autospot.com",
    password: str = "password123",
) -> str:
    response = client.post(
        "/usuarios/registro",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _login_usuario(
    client: TestClient,
    email: str = "conductor.http@autospot.com",
    password: str = "password123",
) -> str:
    response = client.post(
        "/usuarios/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _registrar_y_loguear_usuario(
    client: TestClient,
    email: str = "conductor.http@autospot.com",
    password: str = "password123",
) -> tuple[str, str]:
    usuario_id = _registrar_usuario(client=client, email=email, password=password)
    token = _login_usuario(client=client, email=email, password=password)
    return usuario_id, token


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_cliente():
    """
    Helper: monta engine + DB de test + TestClient con dependency override.

    Returns:
        tuple(engine, TestClient context manager).
    """
    engine = _make_test_engine()
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    app.dependency_overrides[get_db] = _override_get_db_factory(TestingSessionLocal)
    return engine, TestClient(app)


# ══════════════════════════════════════════════════════════════════════════════
#  Registro HTTP — Happy path
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1CA2_RegistroDocumentacionHabilitanteHTTP:
    def test_registra_documentacion_devuelve_201(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(client)

                response = client.put(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    json=PAYLOAD_VALIDO,
                    headers=_auth_headers(token),
                )

                assert response.status_code == 201, response.text
                body = response.json()
                assert body["usuario_id"] == usuario_id
                assert body["numero_licencia"] == "LIC-12345678"
                assert body["categoria"] == "B"
                assert body["fecha_emision"] == "2024-01-10"
                assert body["fecha_vencimiento"] == "2029-01-10"
                assert body["foto_licencia_frente_url"] == (
                    "uploads/licencia/12345678/frente.jpg"
                )
                assert body["foto_licencia_dorso_url"] == (
                    "uploads/licencia/12345678/dorso.jpg"
                )
                assert body["estado_validacion"] == "PENDIENTE_REVISION"
                assert "id" in body
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  Errores HTTP — Auth, autorización, payload y conflictos
# ══════════════════════════════════════════════════════════════════════════════
class TestErroresRegistroHTTP:
    def test_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id = _registrar_usuario(
                    client=client,
                    email="cond.no.token@autospot.com",
                )

                response = client.put(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    json=PAYLOAD_VALIDO,
                )

                assert response.status_code == 401, response.text
                assert response.json()["detail"] == "No autenticado"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_recurso_ajeno_devuelve_403(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="cond.owner@autospot.com",
                )

                response = client.put(
                    f"/usuarios/{uuid.uuid4()}/documentacion-habilitante",
                    json=PAYLOAD_VALIDO,
                    headers=_auth_headers(token),
                )

                assert response.status_code == 403, response.text
                assert (
                    response.json()["detail"]
                    == "No puede operar sobre otro usuario"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_documentacion_ya_registrada_devuelve_409(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="cond.duplicado@autospot.com",
                )

                primera = client.put(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    json=PAYLOAD_VALIDO,
                    headers=_auth_headers(token),
                )
                assert primera.status_code == 201

                segunda = client.put(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    json=PAYLOAD_VALIDO,
                    headers=_auth_headers(token),
                )

                assert segunda.status_code == 409, segunda.text
                assert (
                    segunda.json()["detail"]
                    == "Documentacion habilitante ya registrada"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_payload_con_fecha_invalida_devuelve_422(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="cond.fechas@autospot.com",
                )

                response = client.put(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    json={
                        **PAYLOAD_VALIDO,
                        "fecha_emision": "2029-01-10",
                        "fecha_vencimiento": "2024-01-10",
                    },
                    headers=_auth_headers(token),
                )

                assert response.status_code == 422, response.text
                mensajes = [
                    error.get("msg", "")
                    for error in response.json().get("detail", [])
                ]
                assert any(
                    "fecha de vencimiento debe ser posterior" in m for m in mensajes
                ), mensajes
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_payload_con_categoria_invalida_devuelve_422(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="cond.categoria@autospot.com",
                )

                response = client.put(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    json={**PAYLOAD_VALIDO, "categoria": "Z"},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 422, response.text
                mensajes = [
                    error.get("msg", "")
                    for error in response.json().get("detail", [])
                ]
                assert any("Categoria invalida" in m for m in mensajes), mensajes
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  Actualización y obtención HTTP
# ══════════════════════════════════════════════════════════════════════════════
class TestActualizacionYObtencionHTTP:
    def test_actualiza_documentacion_devuelve_200(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="cond.update@autospot.com",
                )

                client.put(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    json=PAYLOAD_VALIDO,
                    headers=_auth_headers(token),
                )

                response = client.put(
                    f"/usuarios/{usuario_id}/documentacion-habilitante/actualizar",
                    json={
                        **PAYLOAD_VALIDO,
                        "numero_licencia": "LIC-99999999",
                        "categoria": "D",
                    },
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert body["numero_licencia"] == "LIC-99999999"
                assert body["categoria"] == "D"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_obtener_documentacion_sin_registro_devuelve_404(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="cond.get.404@autospot.com",
                )

                response = client.get(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 404, response.text
                assert (
                    response.json()["detail"]
                    == "Documentacion habilitante no registrada"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_obtener_documentacion_registrada_devuelve_200(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="cond.get.200@autospot.com",
                )

                client.put(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    json=PAYLOAD_VALIDO,
                    headers=_auth_headers(token),
                )

                response = client.get(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert body["usuario_id"] == usuario_id
                assert body["numero_licencia"] == "LIC-12345678"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
