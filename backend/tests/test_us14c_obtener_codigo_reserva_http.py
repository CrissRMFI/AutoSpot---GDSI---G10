"""
Tests HTTP — US 14C: Obtener código de reserva.
"""
from decimal import Decimal
from datetime import datetime, timedelta, timezone
import uuid
import itertools

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.utils.security import hash_password
from app.models.datos_personales_usuario import DatosPersonalesUsuario
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _login_usuario,
    _registrar_vehiculo,
    _registrar_y_loguear_usuario,
)

_dni_counter = itertools.count(10000000)

def _registrar_datos_personales_directo(engine, usuario_id: str) -> None:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    dni = str(next(_dni_counter))
    with TestingSessionLocal() as db:
        datos = DatosPersonalesUsuario(
            usuario_id=uuid.UUID(usuario_id),
            dni=dni,
            nombre="Carla",
            apellido="Reserva",
            foto_dni_frente_url=f"uploads/dni/{dni}/frente.jpg",
            foto_dni_dorso_url=f"uploads/dni/{dni}/dorso.jpg",
            estado_validacion="APROBADO",
        )
        db.add(datos)
        db.commit()

def _hacer_vehiculo_reservable(engine, vehiculo_id: str) -> None:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == uuid.UUID(vehiculo_id)).first()
        vehiculo.estado_registro = "HABILITADO"
        vehiculo.disponible = True
        vehiculo.precio_por_dia = Decimal("50000.00")
        vehiculo.estacion = "Estación Belgrano"
        vehiculo.patente = "AB123CD"
        db.commit()


def _registrar_admin_directo(engine, email: str = "admin14c@autospot.com") -> None:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        admin = Usuario(
            email=email,
            hashed_password=hash_password("password123"),
            rol="ADMIN",
        )
        db.add(admin)
        db.commit()


def _payload_reserva(vehiculo_id: str) -> dict:
    fin = datetime.now(timezone.utc) + timedelta(days=3)
    return {
        "vehiculo_id": vehiculo_id,
        "fecha_fin": fin.isoformat(),
    }


class TestUS14CHTTP:
    def test_crea_reserva_y_devuelve_codigo(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "prop14c@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                cliente_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente14c@autospot.com",
                )
                _registrar_datos_personales_directo(engine, cliente_id)
                response = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 201, response.text
                body = response.json()
                assert body["codigo_reserva"].startswith("AS-")
                assert body["codigo_verificado_at"] is None
                assert body["estado"] == "CONFIRMADA"
                assert body["estacion_retiro"] == "Estación Belgrano"
                assert body["vehiculo"]["id"] == vehiculo["id"]
                assert body["vehiculo"]["marca"] == "Toyota"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "prop14c3@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])

                response = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                )

                assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_segunda_reserva_activa_devuelve_409(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "prop14c4@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                cliente_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente14c4@autospot.com",
                )
                _registrar_datos_personales_directo(engine, cliente_id)

                primera = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )
                segunda = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )

                assert primera.status_code == 201
                assert segunda.status_code == 409
                assert "reserva activa" in segunda.text.lower()
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_usuario_propietario_devuelve_403(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "prop14c5@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                client.post(
                    "/usuarios/registro",
                    json={
                        "email": "no-cliente14c@autospot.com",
                        "password": "password123",
                        "rol": "PROPIETARIO",
                    },
                )
                token_propietario = _login_usuario(
                    client,
                    "no-cliente14c@autospot.com",
                )

                response = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_propietario),
                )

                assert response.status_code == 403
                assert "CLIENTE" in response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_lista_reservas_del_cliente(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "prop14c6@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                cliente_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente14c6@autospot.com",
                )
                _registrar_datos_personales_directo(engine, cliente_id)

                creacion = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )
                listado = client.get(
                    "/alquiler/reservas",
                    headers=_auth_headers(token_cliente),
                )

                assert creacion.status_code == 201
                assert listado.status_code == 200
                reservas = listado.json()
                assert len(reservas) == 1
                assert reservas[0]["id"] == creacion.json()["id"]
                assert reservas[0]["codigo_reserva"] == creacion.json()["codigo_reserva"]
                assert reservas[0]["codigo_verificado_at"] is None
                assert reservas[0]["vehiculo"]["id"] == vehiculo["id"]
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_verificar_codigo_lo_invalida_una_sola_vez(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "prop14c7@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                _registrar_admin_directo(engine)
                cliente_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente14c7@autospot.com",
                )
                _registrar_datos_personales_directo(engine, cliente_id)
                token_admin = _login_usuario(client, "admin14c@autospot.com")

                creacion = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )
                codigo = creacion.json()["codigo_reserva"]

                primera_lectura = client.post(
                    "/alquiler/reservas/verificar-codigo",
                    json={"codigo_reserva": codigo},
                    headers=_auth_headers(token_admin),
                )
                segunda_lectura = client.post(
                    "/alquiler/reservas/verificar-codigo",
                    json={"codigo_reserva": codigo},
                    headers=_auth_headers(token_admin),
                )

                assert creacion.status_code == 201
                assert primera_lectura.status_code == 200
                assert primera_lectura.json()["codigo_verificado_at"] is not None
                assert segunda_lectura.status_code == 409
                assert "ya fue utilizado" in segunda_lectura.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_creacion_exitosa_sin_reservas_activas(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "prop_regla1@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                
                cliente_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente_regla1@autospot.com",
                )
                _registrar_datos_personales_directo(engine, cliente_id)

                # Cliente sin reservas previas intenta crear una
                response = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )

                # Debe ser exitoso
                assert response.status_code == 201
                body = response.json()
                assert body["estado"] == "CONFIRMADA"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_creacion_falla_por_reserva_activa_del_usuario(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                # Se registran dos vehiculos distintos
                vehiculo1, _ = _registrar_vehiculo(client, "prop_regla2a@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo1["id"])
                
                vehiculo2, _ = _registrar_vehiculo(client, "prop_regla2b@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo2["id"])

                cliente_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente_regla2@autospot.com",
                )
                _registrar_datos_personales_directo(engine, cliente_id)

                # Cliente crea la PRIMERA reserva (activa)
                primera_reserva = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo1["id"]),
                    headers=_auth_headers(token_cliente),
                )
                assert primera_reserva.status_code == 201

                # Cliente intenta crear una SEGUNDA reserva para otro vehiculo
                segunda_reserva = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo2["id"]),
                    headers=_auth_headers(token_cliente),
                )

                # Debe fallar devolviendo codigo HTTP apropiado (ej. 409 Conflict)
                assert segunda_reserva.status_code in [400, 409]
                # Validar la presencia del mensaje solicitado para el frontend en el cuerpo del error
                assert "Ya posees una reserva en curso y debes finalizarla o cancelarla antes de realizar otra" in segunda_reserva.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
