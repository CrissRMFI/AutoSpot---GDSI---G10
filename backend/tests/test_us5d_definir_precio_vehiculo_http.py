"""
Tests de Integración HTTP — US 5D: PATCH /vehiculos/{vehiculo_id}/precio.

Historia de Usuario:
  Como dueño de un auto recién registrado y habilitado,
  quiero establecer el valor de la tarifa de alquiler por día,
  para que mi auto pueda empezar a generar ingresos.

Endpoint:
  PATCH /vehiculos/{vehiculo_id}/precio

Alcance de esta iteración:
  - solo precio por día
  - sin descuentos
  - sin comisión
  - sin precio dinámico
  - sin moneda múltiple
  - sin precio semanal/mensual

Criterios cubiertos inicialmente:
  CA1 → precio mayor a cero permite guardar la tarifa diaria.
"""
from decimal import Decimal
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Imports necesarios para que Base.metadata conozca los modelos en tests.
from app.models.datos_personales_usuario import DatosPersonalesUsuario  # noqa: F401
from app.models.foto_vehiculo import FotoVehiculo  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401
from app.models.vehiculo import Vehiculo  # noqa: F401


TEST_DATABASE_URL = "sqlite:///:memory:"


def _make_test_engine():
    """Crea un engine SQLite en memoria con foreign keys activadas."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


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
            "email": "propietario.us5d.http@autospot.com",
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


def _crear_cliente():
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


def _registrar_vehiculo(client: TestClient) -> dict:
    """
    Helper: registra usuario + vehículo y devuelve el body del vehículo.
    """
    propietario_id = _registrar_usuario(client)

    response = client.post(
        f"/usuarios/{propietario_id}/vehiculos",
        json=_payload_vehiculo_valido(),
    )

    assert response.status_code == 201, (
        f"No se pudo crear vehículo de prueba. "
        f"Status: {response.status_code}. Body: {response.text}"
    )

    return response.json()


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 — Definir precio válido vía HTTP
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1_DefinirPrecioVehiculoHTTP:
    """
    Verifica el happy path HTTP de la US 5D.
    """

    def test_define_precio_por_dia_valido_devuelve_200(self):
        """
        Dado un vehículo existente,
        cuando se envía un precio por día mayor a cero,
        entonces el backend responde 200 y devuelve el precio actualizado.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                vehiculo = _registrar_vehiculo(client)

                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/precio",
                    json={"precio_por_dia": "35000.00"},
                )

                assert response.status_code == 200, (
                    f"Se esperaba 200, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )

                body = response.json()

                assert body["id"] == vehiculo["id"]
                assert Decimal(str(body["precio_por_dia"])) == Decimal("35000.00")
                TestingSessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=engine,
                )

                with TestingSessionLocal() as db:
                    vehiculo_reconsultado = (
                        db.query(Vehiculo)
                        .filter(Vehiculo.id == uuid.UUID(vehiculo["id"]))
                        .first()
                    )

                    assert vehiculo_reconsultado is not None
                    assert vehiculo_reconsultado.precio_por_dia == Decimal("35000.00")
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    
# ══════════════════════════════════════════════════════════════════════════════
#  Error HTTP — Vehículo inexistente
# ══════════════════════════════════════════════════════════════════════════════
class TestErroresDefinirPrecioVehiculoHTTP:
    """
    Verifica que el endpoint traduzca correctamente errores de dominio
    y validaciones de payload a respuestas HTTP.
    """

    def test_vehiculo_inexistente_devuelve_404(self):
        """
        Si vehiculo_id no corresponde a un vehículo existente,
        el endpoint debe responder 404.
        """
        import uuid

        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                vehiculo_id_inexistente = uuid.uuid4()

                response = client.patch(
                    f"/vehiculos/{vehiculo_id_inexistente}/precio",
                    json={"precio_por_dia": "35000.00"},
                )

                assert response.status_code == 404, (
                    f"Se esperaba 404, se recibió {response.status_code}. "
                    f"Body: {response.text}"
                )

                assert response.json()["detail"] == "Vehiculo no encontrado"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_precio_menor_o_igual_a_cero_devuelve_422(self):
        """
        Si precio_por_dia es cero o negativo,
        el endpoint debe responder 422.
        """
        engine, client_context = _crear_cliente()

        try:
            with client_context as client:
                vehiculo = _registrar_vehiculo(client)

                for precio_invalido in ["0.00", "-1.00"]:
                    response = client.patch(
                        f"/vehiculos/{vehiculo['id']}/precio",
                        json={"precio_por_dia": precio_invalido},
                    )

                    assert response.status_code == 422, (
                        f"Se esperaba 422 para precio {precio_invalido}, "
                        f"se recibió {response.status_code}. Body: {response.text}"
                    )

                    errores = response.json().get("detail", [])
                    mensajes = [error.get("msg", "") for error in errores]

                    assert any(
                        "Precio por dia invalido" in mensaje
                        for mensaje in mensajes
                    ), (
                        f"Se esperaba 'Precio por dia invalido', "
                        f"pero se recibió: {mensajes}"
                    )

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
