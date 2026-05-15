"""
Tests de Integración HTTP — US 1U: PUT /usuarios/{usuario_id}/datos-personales.

Metodología: TDD
  - Primero se define el contrato HTTP esperado.
  - Luego se implementa el router hasta hacer pasar los tests.

Estrategia:
  - Se usa TestClient de FastAPI.
  - Cada test corre con una base limpia.
  - Como el endpoint de datos personales está protegido, los tests HTTP
    registran un usuario, hacen login y envían Authorization: Bearer <token>.

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
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from tests.conftest import _make_test_engine

from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
from app.models.token_blacklist import TokenBlacklist  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401


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


def _registrar_usuario(
    client: TestClient,
    email: str = "datos.http@autospot.com",
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
    email: str = "datos.http@autospot.com",
    password: str = "password123",
) -> str:
    """
    Helper: autentica un Usuario y retorna su access token.
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


def _auth_headers(token: str) -> dict:
    """
    Helper: construye headers HTTP de autenticación.
    """
    return {
        "Authorization": f"Bearer {token}",
    }


def _registrar_y_loguear_usuario(
    client: TestClient,
    email: str = "datos.http@autospot.com",
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


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 y CA2 — Registro HTTP exitoso de datos personales y documentación
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1CA2_RegistroDatosPersonalesHTTP:
    """
    Verifica el happy path HTTP de la US 1U.
    """

    def test_registra_datos_personales_y_documentacion_devuelve_201(self):
        """
        Dado un Usuario con cuenta creada y autenticado,
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
                usuario_id, token = _registrar_y_loguear_usuario(client)

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
                    headers=_auth_headers(token),
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


# ══════════════════════════════════════════════════════════════════════════════
#  Errores HTTP — Usuario inexistente, duplicado y payload inválido
# ══════════════════════════════════════════════════════════════════════════════
class TestErroresRegistroDatosPersonalesHTTP:
    """
    Verifica que el endpoint traduzca correctamente errores de dominio
    y validaciones de payload a respuestas HTTP.
    """

    def _crear_cliente(self):
        """
        Helper: crea engine, sesión de test y TestClient configurado.

        Retorna:
            tuple(engine, client_context_manager)
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

    def test_sin_token_devuelve_401(self):
        """
        Si no se envía token,
        el endpoint debe responder 401 antes de ejecutar lógica de negocio.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                usuario_id = _registrar_usuario(
                    client=client,
                    email="datos.sin.token@autospot.com",
                )

                response = client.put(
                    f"/usuarios/{usuario_id}/datos-personales",
                    json={
                        "dni": "00000001",
                        "nombre": "Usuario",
                        "apellido": "Prueba",
                        "foto_dni_frente_url": "uploads/dni/00000001/frente.jpg",
                        "foto_dni_dorso_url": "uploads/dni/00000001/dorso.jpg",
                    },
                )

                assert response.status_code == 401, (
                    f"Se esperaba 401, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )
                assert response.json()["detail"] == "No autenticado"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_usuario_inexistente_con_token_de_otro_usuario_devuelve_403(self):
        """
        Si el path apunta a otro usuario,
        debe responder 403 antes de revelar si ese usuario existe o no.

        Nota de seguridad:
            Antes este test esperaba 404. Con autenticación correcta,
            el sistema no debe permitir consultar/modificar recursos ajenos.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="datos.owner@autospot.com",
                )

                usuario_id_inexistente = uuid.uuid4()

                response = client.put(
                    f"/usuarios/{usuario_id_inexistente}/datos-personales",
                    json={
                        "dni": "00000001",
                        "nombre": "Usuario",
                        "apellido": "Prueba",
                        "foto_dni_frente_url": "uploads/dni/00000001/frente.jpg",
                        "foto_dni_dorso_url": "uploads/dni/00000001/dorso.jpg",
                    },
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

    def test_datos_personales_ya_registrados_devuelve_409(self):
        """
        Si el Usuario ya registró datos personales,
        el segundo intento debe responder 409.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="datos.duplicados@autospot.com",
                )

                payload = {
                    "dni": "00000001",
                    "nombre": "Usuario",
                    "apellido": "Prueba",
                    "foto_dni_frente_url": "uploads/dni/00000001/frente.jpg",
                    "foto_dni_dorso_url": "uploads/dni/00000001/dorso.jpg",
                }

                primera_respuesta = client.put(
                    f"/usuarios/{usuario_id}/datos-personales",
                    json=payload,
                    headers=_auth_headers(token),
                )
                assert primera_respuesta.status_code == 201

                segunda_respuesta = client.put(
                    f"/usuarios/{usuario_id}/datos-personales",
                    json=payload,
                    headers=_auth_headers(token),
                )

                assert segunda_respuesta.status_code == 409, (
                    f"Se esperaba 409, se recibió {segunda_respuesta.status_code}. "
                    f"Body: {segunda_respuesta.text}"
                )
                assert (
                    segunda_respuesta.json()["detail"]
                    == "Datos personales ya registrados"
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_payload_con_campo_obligatorio_vacio_devuelve_422(self):
        """
        Si falta un campo obligatorio o viene vacío,
        FastAPI/Pydantic debe responder 422.

        Nota:
            Se envía token válido porque el endpoint está protegido.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="datos.payload.invalido@autospot.com",
                )

                response = client.put(
                    f"/usuarios/{usuario_id}/datos-personales",
                    json={
                        "dni": "",
                        "nombre": "Usuario",
                        "apellido": "Prueba",
                        "foto_dni_frente_url": "uploads/dni/00000001/frente.jpg",
                        "foto_dni_dorso_url": "uploads/dni/00000001/dorso.jpg",
                    },
                    headers=_auth_headers(token),
                )

                assert response.status_code == 422, (
                    f"Se esperaba 422, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )

                errores = response.json().get("detail", [])
                mensajes = [error.get("msg", "") for error in errores]

                assert any("Campo obligatorio" in mensaje for mensaje in mensajes), (
                    f"Se esperaba mensaje 'Campo obligatorio', "
                    f"pero se recibió: {mensajes}"
                )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()