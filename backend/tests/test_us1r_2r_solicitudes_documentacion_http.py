"""
Tests de Integración HTTP — US 1R y 2R: Solicitudes de documentación pendientes.

Endpoint:
    GET /admin/solicitudes-documentacion

Contrato esperado:
    - Requiere autenticación (JWT).
    - Solo el rol ADMIN puede consultar la cola.
    - 401 si no se envía token.
    - 403 si el usuario autenticado no es ADMIN.
    - 200 con la lista (posiblemente vacía) cuando es ADMIN.
    - Lista ordenada cronológicamente ascendente (US 2R CA1).
"""
import uuid
from datetime import date, datetime, timezone, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductor,
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


def _registrar_admin_directo(testing_session_local, email: str = "admin@autospot.com"):
    """Crea un Usuario con rol ADMIN saltando el registro público."""
    with testing_session_local() as db:
        admin = Usuario(
            email=email,
            hashed_password=hash_password("password123"),
            rol="ADMIN",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)


def _login(client: TestClient, email: str, password: str = "password123") -> str:
    response = client.post(
        "/usuarios/login",
        json={"email": email, "password": password},
    )
    return response.json()["access_token"]


def _crear_cliente_publico(client: TestClient, email: str) -> tuple[str, str]:
    """Crea un CLIENTE público y devuelve (usuario_id, token)."""
    response = client.post(
        "/usuarios/registro",
        json={"email": email, "password": "password123"},
    )
    usuario_id = response.json()["id"]
    token = _login(client, email)
    return usuario_id, token


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _agregar_vehiculo_en_revision(
    testing_session_local,
    propietario_email: str,
    fecha_solicitud: datetime,
    modelo: str = "Corolla",
) -> str:
    with testing_session_local() as db:
        propietario = Usuario(
            email=propietario_email,
            hashed_password=hash_password("password123"),
            rol="PROPIETARIO",
        )
        db.add(propietario)
        db.commit()
        db.refresh(propietario)

        vehiculo = Vehiculo(
            propietario_id=propietario.id,
            marca="Toyota",
            modelo=modelo,
            anio=2020,
            tipo_transmision="AUTOMATICA",
            capacidad=5,
            categoria="SEDAN",
            tipo_combustible="NAFTA",
            pets_friendly=True,
            estado_registro="EN_REVISION",
            created_at=fecha_solicitud,
            updated_at=fecha_solicitud,
        )
        db.add(vehiculo)
        db.commit()
        db.refresh(vehiculo)
        return str(vehiculo.id)


def _agregar_doc_habilitante_pendiente(
    testing_session_local,
    conductor_email: str,
    fecha_solicitud: datetime,
) -> str:
    with testing_session_local() as db:
        conductor = Usuario(
            email=conductor_email,
            hashed_password=hash_password("password123"),
            rol="CLIENTE",
        )
        db.add(conductor)
        db.commit()
        db.refresh(conductor)

        documentacion = DocumentacionHabilitanteConductor(
            usuario_id=conductor.id,
            categoria="B1",
            fecha_emision=date(2024, 1, 1),
            fecha_vencimiento=date(2029, 1, 1),
            foto_licencia_frente_url="uploads/frente.jpg",
            foto_licencia_dorso_url="uploads/dorso.jpg",
            estado_validacion="PENDIENTE_REVISION",
            created_at=fecha_solicitud,
            updated_at=fecha_solicitud,
        )
        db.add(documentacion)
        db.commit()
        db.refresh(documentacion)
        return str(documentacion.id)


# ══════════════════════════════════════════════════════════════════════════════
#  US 1R CA1 — HTTP devuelve solicitudes existentes
# ══════════════════════════════════════════════════════════════════════════════
class TestUS1R_CA1_HTTPRetornaSolicitudes:
    def test_admin_obtiene_solicitudes_pendientes(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(sl)
                _agregar_vehiculo_en_revision(
                    sl,
                    "duenio@autospot.com",
                    datetime.now(timezone.utc) - timedelta(hours=2),
                )
                _agregar_doc_habilitante_pendiente(
                    sl,
                    "conductor@autospot.com",
                    datetime.now(timezone.utc) - timedelta(hours=1),
                )

                token = _login(client, "admin@autospot.com")
                response = client.get(
                    "/admin/solicitudes-documentacion",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert isinstance(body, list)
                assert len(body) == 2
                tipos = {item["tipo"] for item in body}
                assert tipos == {"VEHICULO", "CONDUCTOR"}
                for item in body:
                    assert "recurso_id" in item
                    assert "usuario_id" in item
                    assert "usuario_email" in item
                    assert "estado" in item
                    assert "fecha_solicitud" in item
                    assert "resumen" in item

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  US 1R CA2 — HTTP devuelve lista vacía cuando no hay trámites
# ══════════════════════════════════════════════════════════════════════════════
class TestUS1R_CA2_HTTPListaVacia:
    def test_admin_obtiene_lista_vacia_si_no_hay_pendientes(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(sl)

                token = _login(client, "admin@autospot.com")
                response = client.get(
                    "/admin/solicitudes-documentacion",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                assert response.json() == []

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  US 2R CA1 y CA2 — HTTP devuelve la lista ordenada cronológicamente
# ══════════════════════════════════════════════════════════════════════════════
class TestUS2R_HTTPOrdenCronologico:
    def test_la_cola_se_devuelve_de_mas_antigua_a_mas_reciente(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(sl)

                ayer = datetime.now(timezone.utc) - timedelta(days=1)
                hace_3h = datetime.now(timezone.utc) - timedelta(hours=3)
                hace_30m = datetime.now(timezone.utc) - timedelta(minutes=30)

                id_antiguo = _agregar_vehiculo_en_revision(
                    sl, "antiguo@autospot.com", ayer, modelo="Corolla",
                )
                id_intermedio = _agregar_doc_habilitante_pendiente(
                    sl, "intermedio@autospot.com", hace_3h,
                )
                id_reciente = _agregar_vehiculo_en_revision(
                    sl, "reciente@autospot.com", hace_30m, modelo="Hilux",
                )

                token = _login(client, "admin@autospot.com")
                response = client.get(
                    "/admin/solicitudes-documentacion",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                ids_en_orden = [item["recurso_id"] for item in response.json()]
                assert ids_en_orden == [id_antiguo, id_intermedio, id_reciente]

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ══════════════════════════════════════════════════════════════════════════════
#  Seguridad — auth y autorización
# ══════════════════════════════════════════════════════════════════════════════
class TestSeguridadSolicitudesHTTP:
    def test_sin_token_devuelve_401(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                response = client.get("/admin/solicitudes-documentacion")
                assert response.status_code == 401

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_token_invalido_devuelve_401(self):
        engine, sl, client_context = _crear_cliente()
        try:
            with client_context as client:
                response = client.get(
                    "/admin/solicitudes-documentacion",
                    headers=_auth_headers("token-falso"),
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
                _, token_cliente = _crear_cliente_publico(
                    client, "cliente@autospot.com",
                )
                response = client.get(
                    "/admin/solicitudes-documentacion",
                    headers=_auth_headers(token_cliente),
                )
                assert response.status_code == 403

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
