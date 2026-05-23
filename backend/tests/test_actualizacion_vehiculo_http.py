import uuid

# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
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

    app.dependency_overrides[get_db] = _override_get_db_factory(TestingSessionLocal)
    return engine, TestClient(app)

def _registrar_y_loguear_usuario(client: TestClient, email: str, password: str = "password123") -> tuple[str, str]:
    client.post("/usuarios/registro", json={"email": email, "password": password})
    response = client.post("/usuarios/login", json={"email": email, "password": password})
    return response.json()["id"], response.json()["access_token"]

def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def _crear_vehiculo(client: TestClient, propietario_id: str, token: str) -> str:
    payload = {
        "marca": "Toyota",
        "modelo": "Corolla",
        "anio": 2020,
        "tipo_transmision": "AUTOMATICA",
        "capacidad": 5,
        "categoria": "SEDAN",
        "tipo_combustible": "NAFTA",
        "pets_friendly": True,
        "fotos": [
            {"lado": "FRENTE", "url": "f.jpg", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "TRASERA", "url": "t.jpg", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "LATERAL_IZQUIERDO", "url": "i.jpg", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "LATERAL_DERECHO", "url": "d.jpg", "formato": "jpg", "tamanio_bytes": 100},
            {"lado": "INTERIOR", "url": "int.jpg", "formato": "jpg", "tamanio_bytes": 100},
        ],
    }
    response = client.post(
        f"/usuarios/{propietario_id}/vehiculos",
        json=payload,
        headers=_auth_headers(token),
    )
    return response.json()["id"]

class TestActualizarVehiculoHTTP:
    def test_actualizar_vehiculo_exitoso_devuelve_200(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(client, "test.update@autospot.com")
                vehiculo_id = _crear_vehiculo(client, propietario_id, token)

                payload_update = {
                    "marca": "Toyota",  # Should be ignored by service
                    "modelo": "Corolla", # Should be ignored by service
                    "anio": 2021,
                    "tipo_transmision": "MANUAL",
                    "capacidad": 4,
                    "categoria": "HATCHBACK",
                    "tipo_combustible": "GNC",
                    "pets_friendly": False,
                    "fotos": [
                        {"lado": "FRENTE", "url": "nf.jpg", "formato": "jpg", "tamanio_bytes": 100},
                        {"lado": "TRASERA", "url": "nt.jpg", "formato": "jpg", "tamanio_bytes": 100},
                        {"lado": "LATERAL_IZQUIERDO", "url": "ni.jpg", "formato": "jpg", "tamanio_bytes": 100},
                        {"lado": "LATERAL_DERECHO", "url": "nd.jpg", "formato": "jpg", "tamanio_bytes": 100},
                        {"lado": "INTERIOR", "url": "nint.jpg", "formato": "jpg", "tamanio_bytes": 100},
                    ],
                }

                response = client.put(
                    f"/vehiculos/{vehiculo_id}",
                    json=payload_update,
                    headers=_auth_headers(token)
                )

                assert response.status_code == 200
                data = response.json()
                assert data["anio"] == 2021
                assert data["tipo_transmision"] == "MANUAL"
                assert data["capacidad"] == 4
                assert data["categoria"] == "HATCHBACK"
                assert data["pets_friendly"] is False
                # Verify that marca and modelo were ignored
                assert data["marca"] == "Toyota"
                assert data["modelo"] == "Corolla"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_actualizar_vehiculo_ajeno_devuelve_403(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                prop1, token1 = _registrar_y_loguear_usuario(client, "user1@autospot.com")
                vehiculo_id = _crear_vehiculo(client, prop1, token1)

                _, token2 = _registrar_y_loguear_usuario(client, "user2@autospot.com")

                payload_update = {
                    "marca": "Toyota", "modelo": "Corolla", "anio": 2021,
                    "tipo_transmision": "MANUAL", "capacidad": 4,
                    "categoria": "HATCHBACK", "tipo_combustible": "GNC", "pets_friendly": False,
                    "fotos": [
                        {"lado": "FRENTE", "url": "nf.jpg", "formato": "jpg", "tamanio_bytes": 100},
                        {"lado": "TRASERA", "url": "nt.jpg", "formato": "jpg", "tamanio_bytes": 100},
                        {"lado": "LATERAL_IZQUIERDO", "url": "ni.jpg", "formato": "jpg", "tamanio_bytes": 100},
                        {"lado": "LATERAL_DERECHO", "url": "nd.jpg", "formato": "jpg", "tamanio_bytes": 100},
                        {"lado": "INTERIOR", "url": "nint.jpg", "formato": "jpg", "tamanio_bytes": 100},
                    ],
                }

                response = client.put(
                    f"/vehiculos/{vehiculo_id}",
                    json=payload_update,
                    headers=_auth_headers(token2)
                )

                assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_cambiar_disponibilidad_vehiculo_devuelve_400_si_no_habilitado(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                prop_id, token = _registrar_y_loguear_usuario(client, "disp@autospot.com")
                vehiculo_id = _crear_vehiculo(client, prop_id, token)

                response = client.patch(
                    f"/vehiculos/{vehiculo_id}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token)
                )

                assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_cambiar_disponibilidad_vehiculo_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                response = client.patch(
                    f"/vehiculos/{uuid.uuid4()}/disponibilidad",
                    json={"disponible": True}
                )
                assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
