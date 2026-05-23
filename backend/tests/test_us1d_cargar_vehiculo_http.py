"""
Tests de Integración HTTP — US 1D: POST /usuarios/{propietario_id}/vehiculos.

Endpoint:
  POST /usuarios/{propietario_id}/vehiculos

Contrato actual:
  - El endpoint requiere JWT.
  - El propietario_id de la URL debe coincidir con el sub del token.
  - Un usuario no puede registrar vehículos para otro propietario.
"""
import uuid
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from tests.conftest import _make_test_engine, sembrar_catalogo

from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
from app.models.foto_vehiculo import FotoVehiculo  # noqa: F401
from app.models.marca import Marca, Modelo  # noqa: F401
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

    Siembra el catálogo de marcas/modelos para que la validación de combo
    (delegada al servicio) encuentre datos contra los cuales chequear.
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
    email: str = "propietario.vehiculo.http@autospot.com",
    password: str = "password123",
) -> str:
    """
    Helper: registra un Usuario base usando el endpoint existente de US 5U
    y retorna su id.
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
    email: str = "propietario.vehiculo.http@autospot.com",
    password: str = "password123",
) -> str:
    """
    Helper: autentica un usuario y retorna su access token.
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
    email: str = "propietario.vehiculo.http@autospot.com",
    password: str = "password123",
) -> tuple[str, str]:
    """
    Helper: registra y autentica un usuario.

    Returns:
        tuple(propietario_id, access_token)
    """
    propietario_id = _registrar_usuario(
        client=client,
        email=email,
        password=password,
    )
    token = _login_usuario(
        client=client,
        email=email,
        password=password,
    )
    return propietario_id, token


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


class TestCA6_RegistroVehiculoHTTP:
    """
    Verifica el happy path HTTP de la US 1D.
    """

    def test_registra_vehiculo_con_caracteristicas_y_fotos_devuelve_201(self):
        """
        Dado un propietario existente y autenticado,
        cuando envía características y fotos válidas,
        entonces el backend responde 201 y devuelve el vehículo registrado.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(client)

                response = client.post(
                    f"/usuarios/{propietario_id}/vehiculos",
                    json=_payload_vehiculo_valido(),
                    headers=_auth_headers(token),
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

                assert len(body["fotos"]) == 5
                lados = {foto["lado"] for foto in body["fotos"]}
                assert lados == {
                    "FRENTE",
                    "TRASERA",
                    "LATERAL_IZQUIERDO",
                    "LATERAL_DERECHO",
                    "INTERIOR",
                }

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestErroresRegistroVehiculoHTTP:
    """
    Verifica que el endpoint traduzca correctamente errores de seguridad,
    dominio y validaciones de payload a respuestas HTTP.
    """

    def _assert_422_con_mensaje(
        self,
        client: TestClient,
        propietario_id: str,
        token: str,
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
            headers=_auth_headers(token),
        )

        assert response.status_code == 422, (
            f"Se esperaba 422, se recibió {response.status_code}. "
            f"Body: {response.text}"
        )

        detalle = response.json().get("detail", [])
        # Pydantic devuelve una lista de errores; HTTPException con un str.
        if isinstance(detalle, str):
            mensajes = [detalle]
        else:
            mensajes = [error.get("msg", "") for error in detalle]

        assert any(mensaje_esperado in mensaje for mensaje in mensajes), (
            f"Se esperaba '{mensaje_esperado}', pero se recibió: {mensajes}"
        )

    def test_sin_token_devuelve_401(self):
        """
        Si no se envía token,
        el endpoint debe responder 401.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id = _registrar_usuario(
                    client=client,
                    email="vehiculo.sin.token@autospot.com",
                )

                response = client.post(
                    f"/usuarios/{propietario_id}/vehiculos",
                    json=_payload_vehiculo_valido(),
                )

                assert response.status_code == 401
                assert response.json()["detail"] == "No autenticado"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_propietario_inexistente_con_token_de_otro_usuario_devuelve_403(self):
        """
        Si el path apunta a otro propietario,
        debe responder 403 antes de revelar si ese usuario existe o no.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="vehiculo.owner@autospot.com",
                )

                propietario_id_inexistente = uuid.uuid4()

                response = client.post(
                    f"/usuarios/{propietario_id_inexistente}/vehiculos",
                    json=_payload_vehiculo_valido(),
                    headers=_auth_headers(token),
                )

                assert response.status_code == 403, (
                    f"Se esperaba 403, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )
                assert (
                    response.json()["detail"]
                    == "No puede operar sobre otro usuario"
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_marca_vacia_devuelve_422(self):
        """
        Si falta una característica obligatoria, el endpoint debe responder 422.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="vehiculo.marca.vacia@autospot.com",
                )

                payload = {
                    **_payload_vehiculo_valido(),
                    "marca": "",
                }

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    token=token,
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
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="vehiculo.anio.invalido@autospot.com",
                )

                payload = {
                    **_payload_vehiculo_valido(),
                    "anio": datetime.now().year + 1,
                }

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    token=token,
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
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="vehiculo.foto.invalida@autospot.com",
                )

                payload = _payload_vehiculo_valido()
                payload["fotos"][0]["formato"] = "gif"

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    token=token,
                    payload=payload,
                    mensaje_esperado="Formato de foto invalido",
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_marca_modelo_inexistente_devuelve_422(self):
        """
        Si marca/modelo no existen en el catálogo permitido,
        el endpoint debe responder 422.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="vehiculo.catalogo.invalido@autospot.com",
                )

                payload = {
                    **_payload_vehiculo_valido(),
                    "marca": "MarcaInexistente",
                    "modelo": "ModeloInexistente",
                }

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    token=token,
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
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="vehiculo.pocas.fotos@autospot.com",
                )

                payload = _payload_vehiculo_valido()
                payload["fotos"] = payload["fotos"][:3]

                self._assert_422_con_mensaje(
                    client=client,
                    propietario_id=propietario_id,
                    token=token,
                    payload=payload,
                    mensaje_esperado="Cantidad minima de fotos requerida",
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()