"""
Tests de Integración HTTP — US 1U: PUT /usuarios/{usuario_id}/datos-personales.

Metodología: TDD
  - Primero se define el contrato HTTP esperado.
  - Luego se implementa el router hasta hacer pasar los tests.

Estrategia:
  - Se usa TestClient de FastAPI.
  - El fixture `client` (conftest.py) o `_make_test_engine` proveen PostgreSQL de test.
  - Cada test corre con una base limpia.

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
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from tests.conftest import _make_test_engine

from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
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


def _registrar_usuario(client: TestClient) -> str:
    """
    Helper: registra un Usuario base usando el endpoint existente de US 5U
    y retorna su id.
    """
    response = client.post(
        "/usuarios/registro",
        json={
            "email": "datos.http@autospot.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201, (
        f"No se pudo crear usuario de prueba. "
        f"Status: {response.status_code}. Body: {response.text}"
    )

    return response.json()["id"]


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 y CA2 — Registro HTTP exitoso de datos personales y documentación
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1CA2_RegistroDatosPersonalesHTTP:
    """
    Verifica el happy path HTTP de la US 1U.
    """

    def test_registra_datos_personales_y_documentacion_devuelve_201(self):
        """
        Dado un Usuario con cuenta creada,
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
                usuario_id = _registrar_usuario(client)

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

    def test_usuario_inexistente_devuelve_404(self):
        """
        Si usuario_id no corresponde a una cuenta existente,
        el endpoint debe responder 404.
        """
        import uuid

        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
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

    def test_datos_personales_ya_registrados_devuelve_409(self):
        """
        Si el Usuario ya registró datos personales,
        el segundo intento debe responder 409.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                usuario_id = _registrar_usuario(client)

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
                )
                assert primera_respuesta.status_code == 201

                segunda_respuesta = client.put(
                    f"/usuarios/{usuario_id}/datos-personales",
                    json=payload,
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
        FastAPI/Pydantic debe responder 422 antes de llegar al servicio.
        """
        engine, client_context = self._crear_cliente()

        try:
            with client_context as client:
                usuario_id = _registrar_usuario(client)

                response = client.put(
                    f"/usuarios/{usuario_id}/datos-personales",
                    json={
                        "dni": "",
                        "nombre": "Usuario",
                        "apellido": "Prueba",
                        "foto_dni_frente_url": "uploads/dni/00000001/frente.jpg",
                        "foto_dni_dorso_url": "uploads/dni/00000001/dorso.jpg",
                    },
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
