"""
Tests de Integración HTTP — Agregar fotos a un vehículo y endpoints de upload.

Endpoints cubiertos:
  - POST /vehiculos/{vehiculo_id}/fotos (lado EXTRA y similares)
  - POST /upload/foto-dni       (validación de lado y auth)
  - POST /upload/foto-licencia  (validación de lado y auth)
  - POST /upload/foto-vehiculo  (acepta EXTRA, valida lados inválidos)

Estrategia:
  - Las pruebas que dependen de Cloudinary real NO se ejecutan: solo validamos
    los caminos de error tempranos (lado inválido, sin token) que se resuelven
    antes de invocar al SDK.
"""
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from tests.conftest import _make_test_engine, sembrar_catalogo

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

    seed_session = TestingSessionLocal()
    try:
        sembrar_catalogo(seed_session)
    finally:
        seed_session.close()

    app.dependency_overrides[get_db] = _override_get_db_factory(TestingSessionLocal)
    return engine, TestClient(app)


def _registrar_y_loguear_usuario(
    client: TestClient,
    email: str,
    password: str = "password123",
    rol: str = "PROPIETARIO",
) -> tuple[str, str]:
    response = client.post(
        "/usuarios/registro",
        json={"email": email, "password": password, "rol": rol},
    )
    assert response.status_code == 201, response.text
    usuario_id = response.json()["id"]

    response = client.post(
        "/usuarios/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return usuario_id, response.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _payload_registro_vehiculo():
    return {
        "marca": "Toyota",
        "modelo": "Corolla",
        "anio": 2020,
        "tipo_transmision": "AUTOMATICA",
        "capacidad": 5,
        "categoria": "SEDAN",
        "tipo_combustible": "NAFTA",
        "pets_friendly": True,
        "kilometros": 50000,
        "fotos": [
            {"lado": "FRENTE", "url": "u/frente.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
            {"lado": "TRASERA", "url": "u/trasera.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
            {"lado": "LATERAL_IZQUIERDO", "url": "u/li.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
            {"lado": "LATERAL_DERECHO", "url": "u/ld.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
            {"lado": "INTERIOR", "url": "u/interior.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
        ],
    }


FOTO_EXTRA_PAYLOAD = {
    "lado": "EXTRA",
    "url": "https://cdn.cloudinary.com/autospot/vehiculos/extra-1.jpg",
    "formato": "jpg",
    "tamanio_bytes": 200_000,
}


# ══════════════════════════════════════════════════════════════════════════════
#  POST /vehiculos/{id}/fotos
# ══════════════════════════════════════════════════════════════════════════════
class TestAgregarFotoVehiculoHTTP:
    def _publicar_vehiculo(self, client, propietario_id, token):
        response = client.post(
            f"/usuarios/{propietario_id}/vehiculos",
            json=_payload_registro_vehiculo(),
            headers=_auth_headers(token),
        )
        assert response.status_code == 201, response.text
        return response.json()["id"]

    def test_agrega_foto_extra_devuelve_201(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client, "owner.agregar.foto@autospot.com"
                )
                vehiculo_id = self._publicar_vehiculo(client, propietario_id, token)

                response = client.post(
                    f"/vehiculos/{vehiculo_id}/fotos",
                    json=FOTO_EXTRA_PAYLOAD,
                    headers=_auth_headers(token),
                )

                assert response.status_code == 201, response.text
                body = response.json()
                assert body["vehiculo_id"] == vehiculo_id
                assert body["lado"] == "EXTRA"
                assert body["url"] == FOTO_EXTRA_PAYLOAD["url"]
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                response = client.post(
                    f"/vehiculos/{uuid.uuid4()}/fotos",
                    json=FOTO_EXTRA_PAYLOAD,
                )

                assert response.status_code == 401, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_vehiculo_ajeno_devuelve_403(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token_owner = _registrar_y_loguear_usuario(
                    client, "owner.foto@autospot.com"
                )
                vehiculo_id = self._publicar_vehiculo(client, propietario_id, token_owner)

                _, token_otro = _registrar_y_loguear_usuario(
                    client, "intruso.foto@autospot.com"
                )

                response = client.post(
                    f"/vehiculos/{vehiculo_id}/fotos",
                    json=FOTO_EXTRA_PAYLOAD,
                    headers=_auth_headers(token_otro),
                )

                assert response.status_code == 403, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_vehiculo_inexistente_devuelve_404(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client, "owner.foto.404@autospot.com"
                )

                response = client.post(
                    f"/vehiculos/{uuid.uuid4()}/fotos",
                    json=FOTO_EXTRA_PAYLOAD,
                    headers=_auth_headers(token),
                )

                assert response.status_code == 404, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_lado_invalido_devuelve_422(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client, "owner.foto.422@autospot.com"
                )
                vehiculo_id = self._publicar_vehiculo(client, propietario_id, token)

                response = client.post(
                    f"/vehiculos/{vehiculo_id}/fotos",
                    json={**FOTO_EXTRA_PAYLOAD, "lado": "DEBAJO"},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 422, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  Validaciones de los endpoints de upload (sin Cloudinary real)
# ══════════════════════════════════════════════════════════════════════════════
class TestUploadAuthYLado:
    def test_foto_dni_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                response = client.post(
                    "/upload/foto-dni?lado=FRENTE",
                    files={"archivo": ("dni.jpg", b"x", "image/jpeg")},
                )
                assert response.status_code == 401, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_foto_dni_lado_invalido_devuelve_400(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client, "owner.dni.400@autospot.com"
                )

                response = client.post(
                    "/upload/foto-dni?lado=LATERAL",
                    headers=_auth_headers(token),
                    files={"archivo": ("dni.jpg", b"x", "image/jpeg")},
                )
                assert response.status_code == 400, response.text
                assert "Lado inválido" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_foto_licencia_lado_invalido_devuelve_400(self):
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client, "owner.lic.400@autospot.com"
                )

                response = client.post(
                    "/upload/foto-licencia?lado=COSTADO",
                    headers=_auth_headers(token),
                    files={"archivo": ("lic.jpg", b"x", "image/jpeg")},
                )
                assert response.status_code == 400, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_foto_vehiculo_acepta_lado_extra_en_validacion_query(self):
        """
        El query-param `lado=EXTRA` debe pasar la validación de lados
        permitidos (antes habría dado 400). El upload real a Cloudinary
        no se ejercita en estos tests.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client, "owner.vehfoto.extra@autospot.com"
                )

                response = client.post(
                    "/upload/foto-vehiculo?lado=EXTRA",
                    headers=_auth_headers(token),
                    files={"archivo": ("e.jpg", b"x", "image/jpeg")},
                )

                # El 400 que rechaza el lado ya no debería ocurrir.
                assert response.status_code != 400 or (
                    "Lado inválido" not in response.json().get("detail", "")
                ), response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
