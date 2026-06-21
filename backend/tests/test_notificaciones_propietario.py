"""
Tests de integración — Notificaciones al propietario por resolución de vehículo.
"""
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.notificacion import Notificacion
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.services.solicitud_documentacion import resolver_solicitud
from app.utils.security import hash_password
from tests.conftest import _make_test_engine, sembrar_catalogo


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
    return engine, TestingSessionLocal, TestClient(app)


def _crear_usuario_directo(testing_session_local, email: str, rol: str) -> str:
    with testing_session_local() as db:
        usuario = Usuario(
            email=email,
            hashed_password=hash_password("password123"),
            rol=rol,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return str(usuario.id)


def _login(client: TestClient, email: str) -> str:
    response = client.post(
        "/usuarios/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_vehiculo_en_revision(testing_session_local, propietario_id: str) -> str:
    with testing_session_local() as db:
        vehiculo = Vehiculo(
            propietario_id=uuid.UUID(propietario_id),
            marca="Toyota",
            modelo="Corolla",
            anio=2020,
            tipo_transmision="AUTOMATICA",
            capacidad=5,
            categoria="SEDAN",
            tipo_combustible="NAFTA",
            pets_friendly=True,
            kilometros=50000,
            estado_registro="EN_REVISION",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(vehiculo)
        db.commit()
        db.refresh(vehiculo)
        return str(vehiculo.id)


def _crear_vehiculo_pendiente_documentacion(
    testing_session_local,
    propietario_id: str,
) -> str:
    with testing_session_local() as db:
        vehiculo = Vehiculo(
            propietario_id=uuid.UUID(propietario_id),
            marca="Toyota",
            modelo="Etios",
            anio=2021,
            tipo_transmision="MANUAL",
            capacidad=5,
            categoria="HATCHBACK",
            tipo_combustible="NAFTA",
            pets_friendly=False,
            kilometros=50000,
            estado_registro="PENDIENTE_DOCUMENTACION",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(vehiculo)
        db.commit()
        db.refresh(vehiculo)
        return str(vehiculo.id)


def _resolver_vehiculo(
    testing_session_local,
    vehiculo_id: str,
    aprobada: bool,
    motivo: str | None = None,
) -> None:
    with testing_session_local() as db:
        resolver_solicitud(
            db=db,
            tipo="VEHICULO",
            recurso_id=uuid.UUID(vehiculo_id),
            aprobada=aprobada,
            motivo_rechazo=motivo,
        )


def _payload_documentacion_valido() -> dict:
    return {
        "patente": "ABC123",
        "chasis": "CHASIS123",
        "motor": "MOTOR123",
        "titular": "Juan Propietario",
        "cedula": "cedula.pdf",
        "poliza": "poliza.pdf",
        "vtv": "vtv.pdf",
        "estacion": "Palermo",
        "telefono": "1122334455",
        "descripcion": "Documentación cargada para revisión.",
    }


class TestNotificacionesPropietario:
    def test_propietario_ve_notificacion_de_auto_habilitado_y_luego_desaparece(self):
        engine, session_local, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_id = _crear_usuario_directo(
                    session_local,
                    "propietario.notificacion@autospot.com",
                    "PROPIETARIO",
                )
                vehiculo_id = _crear_vehiculo_en_revision(session_local, propietario_id)

                _resolver_vehiculo(session_local, vehiculo_id, aprobada=True)

                token = _login(client, "propietario.notificacion@autospot.com")
                response = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert len(body) == 1
                assert body[0]["tipo"] == "VEHICULO_HABILITADO"
                assert body[0]["recurso_id"] == vehiculo_id
                assert body[0]["vista_at"] is None

                response_vista = client.post(
                    f"/notificaciones/{body[0]['id']}/vista",
                    headers=_auth_headers(token),
                )
                assert response_vista.status_code == 204, response_vista.text

                response_despues = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token),
                )
                assert response_despues.status_code == 200, response_despues.text
                assert response_despues.json() == []
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechazo_de_vehiculo_notifica_motivo_al_propietario(self):
        engine, session_local, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_id = _crear_usuario_directo(
                    session_local,
                    "propietario.rechazo@autospot.com",
                    "PROPIETARIO",
                )
                vehiculo_id = _crear_vehiculo_en_revision(session_local, propietario_id)
                motivo = "La póliza no coincide con la patente informada."

                _resolver_vehiculo(
                    session_local,
                    vehiculo_id,
                    aprobada=False,
                    motivo=motivo,
                )

                token = _login(client, "propietario.rechazo@autospot.com")
                response = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert len(body) == 1
                assert body[0]["tipo"] == "VEHICULO_RECHAZADO"
                assert motivo in body[0]["mensaje"]

                with session_local() as db:
                    notificacion = db.query(Notificacion).first()
                    assert notificacion.usuario_id == uuid.UUID(propietario_id)
                    assert notificacion.recurso_id == uuid.UUID(vehiculo_id)
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_recordatorio_documentacion_pendiente_persiste_hasta_subir_documentacion(self):
        engine, session_local, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_id = _crear_usuario_directo(
                    session_local,
                    "propietario.pendiente@autospot.com",
                    "PROPIETARIO",
                )
                vehiculo_id = _crear_vehiculo_pendiente_documentacion(
                    session_local,
                    propietario_id,
                )
                token = _login(client, "propietario.pendiente@autospot.com")

                response = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert len(body) == 1
                assert body[0]["tipo"] == "VEHICULO_DOCUMENTACION_PENDIENTE"
                assert body[0]["recurso_id"] == vehiculo_id

                response_vista = client.post(
                    f"/notificaciones/{body[0]['id']}/vista",
                    headers=_auth_headers(token),
                )
                assert response_vista.status_code == 204, response_vista.text

                response_persistente = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token),
                )
                assert response_persistente.status_code == 200, response_persistente.text
                assert len(response_persistente.json()) == 1

                response_documentacion = client.patch(
                    f"/vehiculos/{vehiculo_id}/documentacion",
                    json=_payload_documentacion_valido(),
                    headers=_auth_headers(token),
                )
                assert response_documentacion.status_code == 200, response_documentacion.text
                assert response_documentacion.json()["estado_registro"] == "EN_REVISION"

                response_final = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token),
                )
                assert response_final.status_code == 200, response_final.text
                assert response_final.json() == []
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
