"""
Tests de Integración HTTP — US 2C: Visualizar estado solicitud de habilitación.

Endpoint bajo prueba:
    GET /usuarios/{usuario_id}/documentacion-habilitante

Criterios de Aceptación cubiertos:
  ┌─────┬──────────────────────────────────────────────────────────────────┐
  │ CA  │ Descripción                                                      │
  ├─────┼──────────────────────────────────────────────────────────────────┤
  │ CA1 │ Conductor consulta y ve "PENDIENTE_REVISION"                     │
  │ CA2 │ Conductor rechazado ve estado + motivo_rechazo                   │
  │ CA1 │ Conductor consulta y ve "APROBADO"                               │
  └─────┴──────────────────────────────────────────────────────────────────┘

Estrategia:
    1. Se registra un usuario y su documentación habilitante vía endpoints HTTP.
    2. Se manipula el estado directamente en la DB de test (simulando la acción
       de un administrador) para cada escenario.
    3. Se consulta el endpoint GET y se valida la respuesta.
"""
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.documentacion_habilitante_conductor import (  # noqa: F401
    DocumentacionHabilitanteConductor,
    EstadoHabilitacion,
)
from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
from app.models.token_blacklist import TokenBlacklist  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401
from tests.conftest import _make_test_engine


PAYLOAD_DOCUMENTACION = {
    "categoria": "B1",
    "fecha_emision": "2024-01-10",
    "fecha_vencimiento": "2029-01-10",
    "foto_licencia_frente_url": "uploads/licencia/us2c/frente.jpg",
    "foto_licencia_dorso_url": "uploads/licencia/us2c/dorso.jpg",
}


# ── Helpers (misma convención que test_us1c_documentacion_habilitante_http) ───


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
    email: str = "conductor.us2c@autospot.com",
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
    email: str = "conductor.us2c@autospot.com",
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
    email: str = "conductor.us2c@autospot.com",
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
        tuple(engine, TestingSessionLocal, TestClient context manager).
        Se incluye TestingSessionLocal para poder manipular la DB en los tests.
    """
    engine = _make_test_engine()
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    app.dependency_overrides[get_db] = _override_get_db_factory(TestingSessionLocal)
    return engine, TestingSessionLocal, TestClient(app)


def _registrar_documentacion(client: TestClient, usuario_id: str, token: str) -> dict:
    """Registra la documentación habilitante vía HTTP y retorna el body."""
    response = client.put(
        f"/usuarios/{usuario_id}/documentacion-habilitante",
        json=PAYLOAD_DOCUMENTACION,
        headers=_auth_headers(token),
    )
    assert response.status_code == 201, response.text
    return response.json()


def _cambiar_estado_en_db(
    session_local,
    usuario_id: str,
    nuevo_estado: EstadoHabilitacion,
    motivo_rechazo: str | None = None,
):
    """
    Simula la acción del administrador cambiando el estado directamente en DB.
    En producción esto será un endpoint de admin (historia futura).
    """
    db = session_local()
    try:
        doc = (
            db.query(DocumentacionHabilitanteConductor)
            .filter(
                DocumentacionHabilitanteConductor.usuario_id
                == uuid.UUID(usuario_id)
            )
            .first()
        )
        assert doc is not None, "La documentación debería existir en DB."

        doc.estado_validacion = nuevo_estado
        doc.motivo_rechazo = motivo_rechazo
        db.commit()
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 — Conductor consulta y ve "PENDIENTE_REVISION"
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1_EstadoPendienteRevision:
    def test_conductor_recibe_estado_pendiente_revision_al_consultar(self):
        """
        Dado que envié mi solicitud de habilitación,
        cuando consulto mi documentación habilitante,
        entonces el sistema muestra "PENDIENTE_REVISION".
        """
        engine, session_local, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="conductor.pendiente@autospot.com",
                )

                # Registrar documentación (estado inicial = PENDIENTE_REVISION)
                _registrar_documentacion(client, usuario_id, token)

                # Consultar estado
                response = client.get(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert body["estado_validacion"] == "PENDIENTE_REVISION"
                assert body.get("motivo_rechazo") is None
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  CA2 — Conductor rechazado ve estado + motivo_rechazo
# ══════════════════════════════════════════════════════════════════════════════
class TestCA2_EstadoRechazadoConMotivo:
    def test_conductor_rechazado_recibe_estado_y_motivo(self):
        """
        Dado que mi solicitud fue "Rechazada",
        cuando accedo al detalle,
        entonces visualizo el motivo del administrador.
        """
        engine, session_local, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="conductor.rechazado@autospot.com",
                )

                _registrar_documentacion(client, usuario_id, token)

                # Simular rechazo por administrador
                motivo = "La foto del frente de la licencia es ilegible."
                _cambiar_estado_en_db(
                    session_local,
                    usuario_id,
                    EstadoHabilitacion.RECHAZADO,
                    motivo_rechazo=motivo,
                )

                # Consultar estado
                response = client.get(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert body["estado_validacion"] == "RECHAZADO"
                assert body["motivo_rechazo"] == motivo
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_conductor_rechazado_sin_motivo_devuelve_null(self):
        """
        Caso borde: si el admin rechaza sin motivo, motivo_rechazo es null.
        """
        engine, session_local, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="conductor.rechazado.sinmotivo@autospot.com",
                )

                _registrar_documentacion(client, usuario_id, token)

                _cambiar_estado_en_db(
                    session_local,
                    usuario_id,
                    EstadoHabilitacion.RECHAZADO,
                    motivo_rechazo=None,
                )

                response = client.get(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert body["estado_validacion"] == "RECHAZADO"
                assert body["motivo_rechazo"] is None
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 — Conductor consulta y ve "APROBADO"
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1_EstadoAprobado:
    def test_conductor_aprobado_recibe_estado_aprobado(self):
        """
        Dado que envié mi solicitud de habilitación y fue aprobada,
        cuando consulto mi documentación habilitante,
        entonces el sistema muestra "APROBADO".
        """
        engine, session_local, client_context = _crear_cliente()

        try:
            with client_context as client:
                usuario_id, token = _registrar_y_loguear_usuario(
                    client=client,
                    email="conductor.aprobado@autospot.com",
                )

                _registrar_documentacion(client, usuario_id, token)

                # Simular aprobación por administrador
                _cambiar_estado_en_db(
                    session_local,
                    usuario_id,
                    EstadoHabilitacion.APROBADO,
                )

                # Consultar estado
                response = client.get(
                    f"/usuarios/{usuario_id}/documentacion-habilitante",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert body["estado_validacion"] == "APROBADO"
                assert body["motivo_rechazo"] is None
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
