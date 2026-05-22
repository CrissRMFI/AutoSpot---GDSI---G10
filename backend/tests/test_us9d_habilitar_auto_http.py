"""
Tests de Integración HTTP — US 9D: Habilitar/Deshabilitar Auto en el momento.

Endpoint propuesto:
  PATCH /vehiculos/{vehiculo_id}/disponibilidad

Contrato esperado:
  - Requiere autenticación (JWT).
  - Permite actualizar el estado de disponibilidad del vehículo.
  - Valida que el vehículo esté en estado "HABILITADO".
  - Valida que no haya reservas en curso al intentar deshabilitar.
"""
from decimal import Decimal
import uuid
from unittest.mock import patch

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
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    seed_session = TestingSessionLocal()
    try:
        sembrar_catalogo(seed_session)
    finally:
        seed_session.close()
    app.dependency_overrides[get_db] = _override_get_db_factory(TestingSessionLocal)
    return engine, TestClient(app)


def _registrar_usuario(client: TestClient, email: str = "us9d@autospot.com", password: str = "password123") -> str:
    response = client.post("/usuarios/registro", json={"email": email, "password": password})
    return response.json()["id"]


def _login_usuario(client: TestClient, email: str = "us9d@autospot.com", password: str = "password123") -> str:
    response = client.post("/usuarios/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def _registrar_y_loguear_usuario(client: TestClient, email: str = "us9d@autospot.com", password: str = "password123") -> tuple[str, str]:
    usuario_id = _registrar_usuario(client=client, email=email, password=password)
    token = _login_usuario(client=client, email=email, password=password)
    return usuario_id, token


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _payload_vehiculo_valido():
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
            {"lado": "FRENTE", "url": "url1", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "TRASERA", "url": "url2", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "LATERAL_IZQUIERDO", "url": "url3", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "LATERAL_DERECHO", "url": "url4", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "INTERIOR", "url": "url5", "formato": "jpg", "tamanio_bytes": 100},
        ],
    }


def _registrar_vehiculo(client: TestClient, email: str = "us9d@autospot.com") -> tuple[dict, str]:
    propietario_id, token = _registrar_y_loguear_usuario(client, email=email)
    response = client.post(
        f"/usuarios/{propietario_id}/vehiculos",
        json=_payload_vehiculo_valido(),
        headers=_auth_headers(token),
    )
    return response.json(), token


def _forzar_estado_vehiculo(engine, vehiculo_id: str, estado: str):
    """Helper para cambiar el estado de registro directamente en DB para los tests."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == uuid.UUID(vehiculo_id)).first()
        if vehiculo:
            vehiculo.estado_registro = estado
            db.commit()


class TestCA1_HabilitarAutoDisponibleHTTP:
    def test_ca1_cambiar_a_disponible_exitoso(self):
        """
        CA 1: Dado que mi auto está registrado y habilitado,
        cuando cambio el estado a "Disponible",
        entonces mi auto pasa al estado disponible para alquiler.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca1@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "HABILITADO")

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, f"Error: {response.text}"
                body = response.json()
                assert body["disponible"] is True
                assert body["id"] == vehiculo["id"]

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestCA2_DeshabilitarAutoHTTP:
    def test_ca2_cambiar_a_no_disponible_exitoso(self):
        """
        CA 2: Dado que mi auto está registrado y habilitado,
        cuando cambio el estado a "No Disponible",
        entonces mi auto pasa al estado no disponible.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca2@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "HABILITADO")

                # Primero lo ponemos disponible
                client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token),
                )

                # Luego probamos cambiar a no disponible
                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": False},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, f"Error: {response.text}"
                body = response.json()
                assert body["disponible"] is False

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestCA3_VehiculoNoHabilitadoHTTP:
    def test_ca3_intento_cambiar_disponibilidad_en_auto_no_habilitado(self):
        """
        CA 3: Dado que mi auto está registrado pero pendiente de habilitación,
        cuando intento cambiar el estado de disponibilidad,
        entonces el sistema informa que mi auto aún no fue habilitado.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca3@autospot.com")
                # Por defecto al registrarse está en PENDIENTE_DOCUMENTACION

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token),
                )

                assert response.status_code in [400, 403, 409], f"Status incorrecto: {response.status_code}"
                
                # Verificamos mensaje de error según CA 3
                mensaje_error = response.text.lower()
                assert "auto aún no fue habilitado" in mensaje_error or "auto aun no fue habilitado" in mensaje_error, (
                    f"Mensaje de error inesperado: {response.text}"
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestCA4_VehiculoConReservaHTTP:
    # Asumimos que existirá una función en el servicio o dependencias que verifique alquileres
    @patch("app.services.vehiculo.verificar_alquileres_activos", return_value=True, create=True)
    def test_ca4_deshabilitar_auto_con_reserva_activa(self, mock_alquileres):
        """
        CA 4: Dado que el auto tiene un alquiler confirmado para este momento,
        cuando intento cambiar el estado a "No Disponible",
        entonces el sistema muestra un error especifico.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca4@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "HABILITADO")

                # Lo ponemos disponible primero
                # Anulamos temporalmente el mock para que permita habilitarlo
                mock_alquileres.return_value = False
                client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token),
                )

                # Restauramos el mock para simular que ahora sí tiene alquiler
                mock_alquileres.return_value = True

                # Intentamos deshabilitarlo mientras tiene alquiler
                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": False},
                    headers=_auth_headers(token),
                )

                assert response.status_code in [400, 403, 409], f"Status incorrecto: {response.status_code}"
                
                # CA 4 string exacto
                mensaje_esperado = "no es posible deshabilitar el auto mientras haya una reserva o alquiler en curso"
                assert mensaje_esperado in response.text.lower(), (
                    f"Mensaje de error esperado no encontrado: {response.text}"
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestSeguridad_CambiarDisponibilidadHTTP:
    def test_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "seguridad1@autospot.com")

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                )
                assert response.status_code == 401

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_usuario_ajeno_devuelve_403(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "propietario@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "HABILITADO")

                # Creamos otro usuario malicioso
                _, token_ajeno = _registrar_y_loguear_usuario(client, "malicioso@autospot.com")

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token_ajeno),
                )
                assert response.status_code == 403

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_vehiculo_inexistente_devuelve_404(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(client, "seguridad3@autospot.com")

                vehiculo_id_inexistente = str(uuid.uuid4())
                response = client.patch(
                    f"/vehiculos/{vehiculo_id_inexistente}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token),
                )
                assert response.status_code == 404

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
