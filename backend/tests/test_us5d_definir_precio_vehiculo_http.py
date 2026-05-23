"""
Tests de Integración HTTP — US 5D: PATCH /vehiculos/{vehiculo_id}/precio.

Endpoint:
  PATCH /vehiculos/{vehiculo_id}/precio

Contrato actual:
  - El endpoint requiere JWT.
  - Solo el propietario del vehículo puede definir su precio.
  - Si el vehículo no existe, responde 404.
"""
from decimal import Decimal
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
    """Crea un override para la dependency get_db usando la sesión de test."""
    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    return override_get_db


def _crear_cliente():
    """
    Helper: crea engine, sesión de test y TestClient configurado.
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

    app.dependency_overrides[get_db] = _override_get_db_factory(
        TestingSessionLocal
    )

    return engine, TestClient(app)


def _registrar_usuario(
    client: TestClient,
    email: str = "propietario.us5d.http@autospot.com",
    password: str = "password123",
) -> str:
    """
    Helper: registra un Usuario base y retorna su id.
    """
    response = client.post(
        "/usuarios/registro",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201, (
        f"No se pudo crear usuario de prueba. "
        f"Status: {response.status_code}. Body: {response.text}"
    )

    return response.json()["id"]


def _login_usuario(
    client: TestClient,
    email: str = "propietario.us5d.http@autospot.com",
    password: str = "password123",
) -> str:
    """
    Helper: autentica un Usuario y retorna access token.
    """
    response = client.post(
        "/usuarios/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200, (
        f"No se pudo autenticar usuario de prueba. "
        f"Status: {response.status_code}. Body: {response.text}"
    )

    return response.json()["access_token"]


def _registrar_y_loguear_usuario(
    client: TestClient,
    email: str = "propietario.us5d.http@autospot.com",
    password: str = "password123",
) -> tuple[str, str]:
    """
    Helper: registra y autentica un usuario.

    Returns:
        tuple(usuario_id, access_token)
    """
    usuario_id = _registrar_usuario(
        client=client,
        email=email,
        password=password,
    )
    token = _login_usuario(
        client=client,
        email=email,
        password=password,
    )
    return usuario_id, token


def _auth_headers(token: str) -> dict:
    """
    Helper: construye headers HTTP de autenticación.
    """
    return {
        "Authorization": f"Bearer {token}",
    }


def _payload_vehiculo_valido():
    """Payload HTTP válido para registrar un vehículo."""
    return {
        "marca": "Toyota",
        "modelo": "Corolla",
        "anio": 2020,
        "tipo_transmision": "AUTOMATICA",
        "capacidad": 5,
        "categoria": "SEDAN",
        "tipo_combustible": "NAFTA",
        "pets_friendly": True,
        "fotos": [
            {
                "lado": "FRENTE",
                "url": "uploads/vehiculos/corolla/frente.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "TRASERA",
                "url": "uploads/vehiculos/corolla/trasera.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "LATERAL_IZQUIERDO",
                "url": "uploads/vehiculos/corolla/lateral_izquierdo.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "LATERAL_DERECHO",
                "url": "uploads/vehiculos/corolla/lateral_derecho.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "INTERIOR",
                "url": "uploads/vehiculos/corolla/interior.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
        ],
    }


def _registrar_vehiculo(client: TestClient) -> tuple[dict, str]:
    """
    Helper: registra usuario + vehículo y devuelve body del vehículo + token.
    """
    propietario_id, token = _registrar_y_loguear_usuario(client)

    response = client.post(
        f"/usuarios/{propietario_id}/vehiculos",
        json=_payload_vehiculo_valido(),
        headers=_auth_headers(token),
    )

    assert response.status_code == 201, (
        f"No se pudo crear vehículo de prueba. "
        f"Status: {response.status_code}. Body: {response.text}"
    )

    return response.json(), token


class TestCA1_DefinirPrecioVehiculoHTTP:
    """
    Verifica el happy path HTTP de la US 5D.
    """

    def test_define_precio_por_dia_valido_devuelve_200(self):
        """
        Dado un vehículo existente y token del propietario,
        cuando se envía un precio por día mayor a cero,
        entonces el backend responde 200 y devuelve el precio actualizado.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client)

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/precio",
                    json={"precio_por_dia": "35000.00"},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, (
                    f"Se esperaba 200, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )

                body = response.json()

                assert body["id"] == vehiculo["id"]
                assert Decimal(str(body["precio_por_dia"])) == Decimal("35000.00")

                TestingSessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=engine,
                )

                with TestingSessionLocal() as db:
                    vehiculo_reconsultado = (
                        db.query(Vehiculo)
                        .filter(Vehiculo.id == uuid.UUID(vehiculo["id"]))
                        .first()
                    )

                    assert vehiculo_reconsultado is not None
                    assert vehiculo_reconsultado.precio_por_dia == Decimal("35000.00")

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestErroresDefinirPrecioVehiculoHTTP:
    """
    Verifica errores HTTP de precio.
    """

    def test_sin_token_devuelve_401(self):
        """
        Si no se envía token,
        el endpoint debe responder 401.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client)

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/precio",
                    json={"precio_por_dia": "35000.00"},
                )

                assert response.status_code == 401
                assert response.json()["detail"] == "No autenticado"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_vehiculo_inexistente_devuelve_404(self):
        """
        Si vehiculo_id no corresponde a un vehículo existente,
        el endpoint debe responder 404.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="precio.vehiculo.inexistente@autospot.com",
                )

                vehiculo_id_inexistente = uuid.uuid4()

                response = client.patch(
                    f"/vehiculos/{vehiculo_id_inexistente}/precio",
                    json={"precio_por_dia": "35000.00"},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 404, (
                    f"Se esperaba 404, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )

                assert response.json()["detail"] == "Vehiculo no encontrado"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_precio_menor_o_igual_a_cero_devuelve_422(self):
        """
        Si precio_por_dia es cero o negativo,
        el endpoint debe responder 422.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client)

                for precio_invalido in ["0.00", "-1.00"]:
                    response = client.patch(
                        f"/vehiculos/{vehiculo['id']}/precio",
                        json={"precio_por_dia": precio_invalido},
                        headers=_auth_headers(token),
                    )

                    assert response.status_code == 422, (
                        f"Se esperaba 422 para precio {precio_invalido}, "
                        f"se recibió {response.status_code}. Body: {response.text}"
                    )

                    errores = response.json().get("detail", [])
                    mensajes = [error.get("msg", "") for error in errores]

                    assert any(
                        "Precio por dia invalido" in mensaje
                        for mensaje in mensajes
                    ), (
                        f"Se esperaba 'Precio por dia invalido', "
                        f"pero se recibió: {mensajes}"
                    )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()