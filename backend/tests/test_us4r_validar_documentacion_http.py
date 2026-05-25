import uuid
from datetime import date, datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductor,
    EstadoHabilitacion,
)
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
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
            email="propietario.validador@autospot.com",
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
            email="conductor.validador@autospot.com",
            hashed_password=hash_password("password123"),
            rol="CLIENTE",
        )
        db.add(conductor)
        db.commit()
        db.refresh(conductor)

        ahora = datetime.now(timezone.utc)
        documentacion = DocumentacionHabilitanteConductor(
            usuario_id=conductor.id,
            numero_licencia="LIC-HTTP-4R",
            categoria="B",
            fecha_emision=date(2024, 1, 1),
            fecha_vencimiento=date(2029, 1, 1),
            foto_licencia_frente_url="https://cdn.autospot.test/frente.jpg",
            foto_licencia_dorso_url="https://cdn.autospot.test/dorso.jpg",
            estado_validacion=EstadoHabilitacion.PENDIENTE_REVISION,
            created_at=ahora,
            updated_at=ahora,
        )
        db.add(documentacion)
        db.commit()
        db.refresh(documentacion)
        return str(documentacion.id)


class Test_US4_ValidarDocumentacion:
    def test_admin_aprueba_vehiculo(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "admin.us4r@autospot.com", "ADMIN")
                vehiculo_id = _agregar_vehiculo_documentado(sl)
                token = _login(client, "admin.us4r@autospot.com")

                response = client.post(
                    f"/admin/solicitudes-documentacion/VEHICULO/{vehiculo_id}/aprobar",
                    headers=_auth_headers(token),
                )
                assert response.status_code == 204

                # Verificar en BD
                with sl() as db:
                    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
                    assert vehiculo.estado_registro == "VALIDADO"

                # Verificar que ya no esta en la cola
                res_cola = client.get(
                    "/admin/solicitudes-documentacion", headers=_auth_headers(token)
                )
                assert len(res_cola.json()) == 0
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_admin_rechaza_vehiculo(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "admin.us4r@autospot.com", "ADMIN")
                vehiculo_id = _agregar_vehiculo_documentado(sl)
                token = _login(client, "admin.us4r@autospot.com")

                response = client.post(
                    f"/admin/solicitudes-documentacion/VEHICULO/{vehiculo_id}/rechazar",
                    headers=_auth_headers(token),
                    json={"motivo_rechazo": "Falta firma en cedula"}
                )
                assert response.status_code == 204

                # Verificar en BD
                with sl() as db:
                    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
                    assert vehiculo.estado_registro == "RECHAZADO"
                    assert vehiculo.motivo_rechazo == "Falta firma en cedula"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_admin_aprueba_conductor(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "admin.us4r@autospot.com", "ADMIN")
                doc_id = _agregar_documentacion_conductor(sl)
                token = _login(client, "admin.us4r@autospot.com")

                response = client.post(
                    f"/admin/solicitudes-documentacion/CONDUCTOR/{doc_id}/aprobar",
                    headers=_auth_headers(token),
                )
                assert response.status_code == 204

                with sl() as db:
                    doc = db.query(DocumentacionHabilitanteConductor).filter(DocumentacionHabilitanteConductor.id == doc_id).first()
                    assert doc.estado_validacion == EstadoHabilitacion.APROBADO
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_admin_rechaza_conductor(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "admin.us4r@autospot.com", "ADMIN")
                doc_id = _agregar_documentacion_conductor(sl)
                token = _login(client, "admin.us4r@autospot.com")

                response = client.post(
                    f"/admin/solicitudes-documentacion/CONDUCTOR/{doc_id}/rechazar",
                    headers=_auth_headers(token),
                    json={"motivo_rechazo": "Licencia vencida"}
                )
                assert response.status_code == 204

                with sl() as db:
                    doc = db.query(DocumentacionHabilitanteConductor).filter(DocumentacionHabilitanteConductor.id == doc_id).first()
                    assert doc.estado_validacion == EstadoHabilitacion.RECHAZADO
                    assert doc.motivo_rechazo == "Licencia vencida"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechazo_sin_motivo_falla_validacion(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_usuario_directo(sl, "admin.us4r@autospot.com", "ADMIN")
                vehiculo_id = _agregar_vehiculo_documentado(sl)
                token = _login(client, "admin.us4r@autospot.com")

                response = client.post(
                    f"/admin/solicitudes-documentacion/VEHICULO/{vehiculo_id}/rechazar",
                    headers=_auth_headers(token),
                    json={} # Falta el motivo
                )
                assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
