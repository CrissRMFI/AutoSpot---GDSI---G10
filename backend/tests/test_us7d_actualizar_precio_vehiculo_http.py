"""
Tests de Integración HTTP — US 7D: Actualización de precio del auto.

Endpoint:
  PATCH /vehiculos/{vehiculo_id}/precio

Diferencia con US 5D:
  US 5D prueba la definición inicial del precio.
  US 7D prueba la actualización de un precio ya existente y cubre el caso 403
  (propietario que intenta operar sobre un vehículo ajeno).

Contrato:
  - Requiere JWT.
  - Solo el propietario del vehículo puede actualizar su precio.
  - Sin token              → 401.
  - Vehículo de otro usuario → 403.
  - Vehículo inexistente   → 404.
  - Precio cero o negativo → 422.
"""
from decimal import Decimal
import uuid

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
        autocommit=False, autoflush=False, bind=engine
    )
    app.dependency_overrides[get_db] = _override_get_db_factory(TestingSessionLocal)
    return engine, TestClient(app)


def _registrar_usuario(client: TestClient, email: str, password: str = "password123") -> str:
    response = client.post("/usuarios/registro", json={"email": email, "password": password})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _login_usuario(client: TestClient, email: str, password: str = "password123") -> str:
    response = client.post("/usuarios/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _registrar_y_loguear_usuario(
    client: TestClient,
    email: str,
    password: str = "password123",
) -> tuple[str, str]:
    usuario_id = _registrar_usuario(client, email, password)
    token = _login_usuario(client, email, password)
    return usuario_id, token


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _payload_vehiculo_valido() -> dict:
    return {
        "marca": "Toyota",
        "modelo": "Etios",
        "anio": 2021,
        "tipo_transmision": "MANUAL",
        "capacidad": 5,
        "categoria": "SEDAN",
        "tipo_combustible": "NAFTA",
        "pets_friendly": False,
        "fotos": [
            {"lado": "FRENTE", "url": "uploads/etios/frente.jpg", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "TRASERA", "url": "uploads/etios/trasera.jpg", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "LATERAL_IZQUIERDO", "url": "uploads/etios/lateral_izq.jpg", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "LATERAL_DERECHO", "url": "uploads/etios/lateral_der.jpg", "formato": "jpg", "tamanio_bytes": 100},
        ],
    }


def _registrar_vehiculo_con_precio(
    client: TestClient,
    propietario_id: str,
    token: str,
    precio_inicial: str = "30000.00",
) -> dict:
    """Registra un vehículo y le define un precio inicial (estado post-US 5D)."""
    res = client.post(
        f"/usuarios/{propietario_id}/vehiculos",
        json=_payload_vehiculo_valido(),
        headers=_auth_headers(token),
    )
    assert res.status_code == 201, res.text
    vehiculo = res.json()

    res_precio = client.patch(
        f"/vehiculos/{vehiculo['id']}/precio",
        json={"precio_por_dia": precio_inicial},
        headers=_auth_headers(token),
    )
    assert res_precio.status_code == 200, res_precio.text

    return vehiculo


# ══════════════════════════════════════════════════════════════════════════════
#  Happy path — Actualizar precio ya definido
# ══════════════════════════════════════════════════════════════════════════════
class TestActualizarPrecioHTTP:
    """Verifica el flujo exitoso de actualización de precio (US 7D)."""

    def test_actualiza_precio_existente_devuelve_200(self):
        """
        Dado un vehículo con precio 30000 ya definido,
        cuando el propietario envía precio 50000,
        entonces el backend responde 200 con el precio actualizado.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client, "us7d.actualizar@autospot.com"
                )
                vehiculo = _registrar_vehiculo_con_precio(
                    client, propietario_id, token, "30000.00"
                )

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/precio",
                    json={"precio_por_dia": "50000.00"},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert body["id"] == vehiculo["id"]
                assert Decimal(str(body["precio_por_dia"])) == Decimal("50000.00")
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_precio_persiste_en_base_de_datos(self):
        """
        Tras actualizar el precio, el valor debe estar persistido en la DB.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client, "us7d.persistencia@autospot.com"
                )
                vehiculo = _registrar_vehiculo_con_precio(
                    client, propietario_id, token, "30000.00"
                )

                client.patch(
                    f"/vehiculos/{vehiculo['id']}/precio",
                    json={"precio_por_dia": "75000.00"},
                    headers=_auth_headers(token),
                )

                TestingSessionLocal = sessionmaker(
                    autocommit=False, autoflush=False, bind=engine
                )
                with TestingSessionLocal() as db:
                    vehiculo_db = (
                        db.query(Vehiculo)
                        .filter(Vehiculo.id == uuid.UUID(vehiculo["id"]))
                        .first()
                    )
                    assert vehiculo_db is not None
                    assert vehiculo_db.precio_por_dia == Decimal("75000.00")
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  Errores de contrato HTTP
# ══════════════════════════════════════════════════════════════════════════════
class TestErroresActualizarPrecioHTTP:
    """Verifica los casos de error del contrato HTTP (US 7D)."""

    def test_sin_token_devuelve_401(self):
        """Sin JWT, el endpoint responde 401."""
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client, "us7d.sin.token@autospot.com"
                )
                vehiculo = _registrar_vehiculo_con_precio(
                    client, propietario_id, token
                )

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/precio",
                    json={"precio_por_dia": "50000.00"},
                )

                assert response.status_code == 401
                assert response.json()["detail"] == "No autenticado"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_vehiculo_ajeno_devuelve_403(self):
        """
        Cuando un usuario intenta actualizar el precio de un vehículo ajeno,
        el endpoint responde 403.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token_propietario = _registrar_y_loguear_usuario(
                    client, "us7d.propietario.403@autospot.com"
                )
                vehiculo = _registrar_vehiculo_con_precio(
                    client, propietario_id, token_propietario
                )

                _, token_intruso = _registrar_y_loguear_usuario(
                    client, "us7d.intruso.403@autospot.com"
                )

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/precio",
                    json={"precio_por_dia": "50000.00"},
                    headers=_auth_headers(token_intruso),
                )

                assert response.status_code == 403, (
                    f"Se esperaba 403, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_vehiculo_inexistente_devuelve_404(self):
        """Si vehiculo_id no existe, el endpoint responde 404."""
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client, "us7d.vehiculo.404@autospot.com"
                )

                response = client.patch(
                    f"/vehiculos/{uuid.uuid4()}/precio",
                    json={"precio_por_dia": "50000.00"},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 404
                assert response.json()["detail"] == "Vehiculo no encontrado"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_precio_invalido_devuelve_422(self):
        """Si el nuevo precio es cero o negativo, el endpoint responde 422."""
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client, "us7d.precio.422@autospot.com"
                )
                vehiculo = _registrar_vehiculo_con_precio(
                    client, propietario_id, token
                )

                for precio_invalido in ["0.00", "-100.00"]:
                    response = client.patch(
                        f"/vehiculos/{vehiculo['id']}/precio",
                        json={"precio_por_dia": precio_invalido},
                        headers=_auth_headers(token),
                    )

                    assert response.status_code == 422, (
                        f"Se esperaba 422 para precio {precio_invalido}, "
                        f"se recibió {response.status_code}."
                    )

                    mensajes = [
                        e.get("msg", "") for e in response.json().get("detail", [])
                    ]
                    assert any("Precio por dia invalido" in m for m in mensajes)
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
