"""
Tests HTTP — US 3R: Abrir documentación.

Endpoint bajo prueba:
    GET /admin/solicitudes-documentacion/{tipo}/{recurso_id}
"""
import uuid
from datetime import date, datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductor,
)
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.solicitud_documentacion import (
    TIPO_SOLICITUD_CONDUCTOR,
    TIPO_SOLICITUD_VEHICULO,
)
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


def _crear_usuario_directo(
    testing_session_local,
    email: str,
    rol: str,
) -> None:
    with testing_session_local() as db:
        usuario = Usuario(
            email=email,
            hashed_password=hash_password("password123"),
            rol=rol,
        )
        db.add(usuario)
        db.commit()


def _login(client: TestClient, email: str, password: str = "password123") -> str:
    response = client.post(
        "/usuarios/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _agregar_vehiculo_documentado(testing_session_local) -> str:
    with testing_session_local() as db:
        propietario = Usuario(
            email="propietario.detalle@autospot.com",
            hashed_password=hash_password("password123"),
            rol="PROPIETARIO",
        )
        db.add(propietario)
        db.commit()
        db.refresh(propietario)

        ahora = datetime.now(timezone.utc)
        vehiculo = Vehiculo(
            propietario_id=propietario.id,
            marca="Toyota",
            modelo="Corolla",
            anio=2023,
            tipo_transmision="AUTOMATICA",
            capacidad=5,
            categoria="SEDAN",
            tipo_combustible="NAFTA",
            pets_friendly=True,
            kilometros=50000,
            patente="AB123CD",
            chasis="CHASIS-HTTP",
            motor="MOTOR-HTTP",
            titular="Roberto Garcia",
            cedula="https://cdn.autospot.test/cedula.jpg",
            poliza="https://cdn.autospot.test/poliza.jpg",
            vtv="https://cdn.autospot.test/vtv.jpg",
            estacion="Palermo",
            telefono="+541100000000",
            descripcion="Documentacion completa.",
            estado_registro="EN_REVISION",
            created_at=ahora,
            updated_at=ahora,
        )
        db.add(vehiculo)
        db.commit()
        db.refresh(vehiculo)
        return str(vehiculo.id)


def _agregar_documentacion_conductor(testing_session_local) -> str:
    with testing_session_local() as db:
        conductor = Usuario(
            email="conductor.detalle@autospot.com",
            hashed_password=hash_password("password123"),
            rol="CLIENTE",
        )
        db.add(conductor)
        db.commit()
        db.refresh(conductor)

        ahora = datetime.now(timezone.utc)
        documentacion = DocumentacionHabilitanteConductor(
            usuario_id=conductor.id,
            categoria="B1",
            fecha_emision=date(2024, 1, 1),
            fecha_vencimiento=date(2029, 1, 1),
            foto_licencia_frente_url="https://cdn.autospot.test/frente.jpg",
            foto_licencia_dorso_url="https://cdn.autospot.test/dorso.jpg",
            estado_validacion="PENDIENTE_REVISION",
            created_at=ahora,
            updated_at=ahora,
        )
        db.add(documentacion)
        db.commit()
        db.refresh(documentacion)
        return str(documentacion.id)


class TestUS3RHTTPAbrirDocumentacion:
    def test_admin_abre_detalle_de_vehiculo(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "admin.us3r@autospot.com", "ADMIN")
                vehiculo_id = _agregar_vehiculo_documentado(sl)
                token = _login(client, "admin.us3r@autospot.com")

                response = client.get(
                    f"/admin/solicitudes-documentacion/VEHICULO/{vehiculo_id}",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert body["tipo"] == "VEHICULO"
                assert body["patente"] == "AB123CD"
                assert body["chasis"] == "CHASIS-HTTP"
                assert len(body["documentos"]) == 3
                assert body["documentos"][0]["url"].endswith("cedula.jpg")
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_admin_abre_detalle_de_conductor(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "admin.us3r@autospot.com", "ADMIN")
                documentacion_id = _agregar_documentacion_conductor(sl)
                token = _login(client, "admin.us3r@autospot.com")

                response = client.get(
                    f"/admin/solicitudes-documentacion/CONDUCTOR/{documentacion_id}",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert body["tipo"] == "CONDUCTOR"
                assert body["categoria_licencia"] == "B1"
                assert len(body["documentos"]) == 2
                assert body["documentos"][1]["nombre"] == "Licencia dorso"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestUS3RHTTPSeguridad:
    def test_sin_token_devuelve_401(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                response = client.get(
                    f"/admin/solicitudes-documentacion/VEHICULO/{uuid.uuid4()}"
                )
                assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_usuario_no_admin_devuelve_403(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "cliente.us3r@autospot.com", "CLIENTE")
                token = _login(client, "cliente.us3r@autospot.com")

                response = client.get(
                    f"/admin/solicitudes-documentacion/VEHICULO/{uuid.uuid4()}",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_tipo_invalido_devuelve_400(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "admin.us3r@autospot.com", "ADMIN")
                token = _login(client, "admin.us3r@autospot.com")

                response = client.get(
                    f"/admin/solicitudes-documentacion/OTRO/{uuid.uuid4()}",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_recurso_inexistente_devuelve_404(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "admin.us3r@autospot.com", "ADMIN")
                token = _login(client, "admin.us3r@autospot.com")

                response = client.get(
                    f"/admin/solicitudes-documentacion/VEHICULO/{uuid.uuid4()}",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
