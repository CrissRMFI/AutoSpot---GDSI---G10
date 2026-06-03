"""
Tests HTTP — US 11C: Suministro de información logística de retiro.
"""
from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.estacion import Estacion
from tests.test_us5r_verificar_codigo_reserva_http import _registrar_datos_personales_directo
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _registrar_vehiculo,
    _registrar_y_loguear_usuario,
)
from tests.test_us14c_obtener_codigo_reserva_http import (
    _hacer_vehiculo_reservable,
    _payload_reserva,
)


def _crear_estacion_en_db(engine, nombre: str = "Estación Belgrano") -> Estacion:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        estacion = Estacion(
            nombre=nombre,
            direccion="Av. Siempre Viva 123",
            instrucciones_acceso="Tocar timbre en la reja verde",
            zona="Norte",
            activa=True,
            imagen_url="http://imagen.com/estacion.jpg",
        )
        db.add(estacion)
        db.commit()
        db.refresh(estacion)
        return estacion


class TestUS11CInformacionLogisticaRetiroHTTP:
    def test_ca1_estado_no_formalizado_oculta_logistica(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_estacion_en_db(engine, "Estación Belgrano")
                vehiculo, _ = _registrar_vehiculo(client, "prop11c1@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                
                cliente_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente11c1@autospot.com",
                )
                _registrar_datos_personales_directo(engine, cliente_id)

                # Creamos reserva
                creacion = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )
                assert creacion.status_code == 201
                reserva_id = creacion.json()["id"]

                # Forzamos estado a "PENDIENTE" en DB para probar CA 1
                TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                with TestingSessionLocal() as db:
                    from app.models.reserva import Reserva
                    reserva_db = db.query(Reserva).filter(Reserva.id == uuid.UUID(reserva_id)).first()
                    reserva_db.estado = "PENDIENTE"
                    db.commit()

                # Consultamos el detalle
                detalle = client.get(
                    f"/alquiler/reservas/{reserva_id}",
                    headers=_auth_headers(token_cliente),
                )

                assert detalle.status_code == 200
                data = detalle.json()
                
                # CA 1: Los campos logísticos vienen en null
                assert "estacion_detalle" in data
                assert data["estacion_detalle"] is None
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ca2_estado_habilitado_muestra_logistica(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                estacion_db = _crear_estacion_en_db(engine, "Estación Belgrano")
                vehiculo, _ = _registrar_vehiculo(client, "prop11c2@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                
                cliente_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente11c2@autospot.com",
                )
                _registrar_datos_personales_directo(engine, cliente_id)

                # Creamos reserva (estado por defecto CONFIRMADA)
                creacion = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )
                assert creacion.status_code == 201
                reserva_id = creacion.json()["id"]

                # Consultamos el detalle
                detalle = client.get(
                    f"/alquiler/reservas/{reserva_id}",
                    headers=_auth_headers(token_cliente),
                )

                assert detalle.status_code == 200
                data = detalle.json()
                
                # CA 2: Retorna los datos logísticos correctos unidos de la tabla estaciones
                assert "estacion_detalle" in data
                estacion_detalle = data["estacion_detalle"]
                assert estacion_detalle is not None
                assert estacion_detalle["nombre"] == estacion_db.nombre
                assert estacion_detalle["direccion"] == estacion_db.direccion
                assert estacion_detalle["instrucciones_acceso"] == estacion_db.instrucciones_acceso
                assert estacion_detalle["zona"] == estacion_db.zona
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
