"""
Tests de Integración HTTP — US 1D: POST /usuarios/{propietario_id}/vehiculos.

Historia de Usuario:
  Como dueño de auto,
  quiero agregar las características detalladas y subir fotos de mi auto,
  para el registro del auto en la plataforma.

Endpoint temporal:
  POST /usuarios/{propietario_id}/vehiculos

Nota:
  Se usa propietario_id explícito porque todavía no existe autenticación/JWT
  ni especialización formal del rol Propietario (US2 y US3 aun no las implementan).

Criterios cubiertos inicialmente:
  CA6 → si completo todo correctamente y guardo, la información del auto
        se guarda exitosamente.
"""
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from tests.conftest import _make_test_engine

# Imports necesarios para que Base.metadata conozca los modelos en tests
from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
from app.models.foto_vehiculo import FotoVehiculo  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401
from app.models.vehiculo import Vehiculo  # noqa: F401

from sqlalchemy.orm import sessionmaker


def _override_get_db_factory(testing_session_local):
    """Crea un override para la dependency get_db usando la sesión de test."""
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
            "email": "propietario.vehiculo.http@autospot.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201, (
        f"No se pudo crear usuario de prueba. "
        f"Status: {response.status_code}. Body: {response.text}"
    )

    return response.json()["id"]


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
        ],
    }


class TestCA6_RegistroVehiculoHTTP:
    """
    Verifica el happy path HTTP de la US 1D.
    """

    def test_registra_vehiculo_con_caracteristicas_y_fotos_devuelve_201(self):
        """
        Dado un propietario existente,
        cuando envía características y fotos válidas,
        entonces el backend responde 201 y devuelve el vehículo registrado.
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
                propietario_id = _registrar_usuario(client)

                response = client.post(
                    f"/usuarios/{propietario_id}/vehiculos",
                    json=_payload_vehiculo_valido(),
                )

                assert response.status_code == 201, (
                    f"Se esperaba 201, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )

                body = response.json()

                assert body["propietario_id"] == propietario_id
                assert body["marca"] == "Toyota"
                assert body["modelo"] == "Corolla"
                assert body["anio"] == 2020
                assert body["tipo_transmision"] == "AUTOMATICA"
                assert body["capacidad"] == 5
                assert body["categoria"] == "SEDAN"
                assert body["tipo_combustible"] == "NAFTA"
                assert body["pets_friendly"] is True
                assert body["estado_registro"] == "PENDIENTE_DOCUMENTACION"
                assert "id" in body

                assert len(body["fotos"]) == 4
                lados = {foto["lado"] for foto in body["fotos"]}
                assert lados == {
                    "FRENTE",
                    "TRASERA",
                    "LATERAL_IZQUIERDO",
                    "LATERAL_DERECHO",
                }

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  Errores HTTP — US 1D
# ══════════════════════════════════════════════════════════════════════════════
class TestErroresRegistroVehiculoHTTP:
    """
    Verifica que el endpoint traduzca correctamente errores de dominio
    y validaciones de payload a respuestas HTTP.
    """

    def _crear_cliente(self):
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

        app.dependency_overrides[get_db] = _override_get_db_factory(
            TestingSessionLocal
        )

        return engine, TestClient(app)

    def _assert_422_con_mensaje(
        self,
        client: TestClient,
        propietario_id: str,
        payload: dict,
        mensaje_esperado: str,
    ) -> None:
        """
        Helper: ejecuta POST /usuarios/{propietario_id}/vehiculos
        y verifica respuesta 422 con mensaje esperado.
        """
        response = client.post(
            f"/usuarios/{propietario_id}/vehiculos",
            json=payload,
        )

        assert response.status_code == 422, (
            f"Se esperaba 422, se recibió {response.status_code}. "
            f"Body: {response.text}"
        )

        errores = response.json().get("detail", [])
        mensajes = [error.get("msg", "") for error in errores]

        assert any(mensaje_esperado in mensaje for mensaje in mensajes), (
            f"Se esperaba '{mensaje_esperado}', pero se recibió: {mensajes}"
        )

    def test_propietario_inexistente_devuelve_404(self):
        """
        Si propietario_id no corresponde a un Usuario existente,
        el endpoint debe responder 404.
        """
        import uuid

        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                propietario_id_inexistente = uuid.uuid4()

                response = client.post(
                    f"/usuarios/{propietario_id_inexistente}/vehiculos",
                    json=_payload_vehiculo_valido(),
                )

                assert response.status_code == 404, (
                    f"Se esperaba 404, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )
                assert response.json()["detail"] == "Usuario no encontrado"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_marca_vacia_devuelve_422(self):
        """
        Si falta una característica obligatoria, el endpoint debe responder 422.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                propietario_id = _registrar_usuario(client)

                payload = {
                    **_payload_vehiculo_valido(),
                    "marca": "",
                }

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    payload=payload,
                    mensaje_esperado="Campo obligatorio",
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_anio_mayor_al_actual_devuelve_422(self):
        """
        Si el año del auto es mayor al actual, el endpoint debe responder 422.
        """
        from datetime import datetime

        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                propietario_id = _registrar_usuario(client)

                payload = {
                    **_payload_vehiculo_valido(),
                    "anio": datetime.now().year + 1,
                }

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    payload=payload,
                    mensaje_esperado="Anio del auto invalido",
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_foto_con_formato_invalido_devuelve_422(self):
        """
        Si una foto tiene formato inválido, el endpoint debe responder 422.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                propietario_id = _registrar_usuario(client)
                payload = _payload_vehiculo_valido()

                payload["fotos"][0] = {
                    **payload["fotos"][0],
                    "formato": "gif",
                }

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    payload=payload,
                    mensaje_esperado="Formato de foto invalido",
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_marca_modelo_inexistente_devuelve_422(self):
        """
        Si la combinación marca/modelo no existe, el endpoint debe responder 422.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                propietario_id = _registrar_usuario(client)

                payload = {
                    **_payload_vehiculo_valido(),
                    "marca": "Toyota",
                    "modelo": "Fiesta",
                }

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    payload=payload,
                    mensaje_esperado="Combinacion marca modelo inexistente",
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_menos_de_cuatro_fotos_devuelve_422(self):
        """
        Si no se cargan cuatro fotos mínimas, el endpoint debe responder 422.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                propietario_id = _registrar_usuario(client)
                payload = _payload_vehiculo_valido()
                payload["fotos"] = payload["fotos"][:3]

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    payload=payload,
                    mensaje_esperado="Cantidad minima de fotos requerida",
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
