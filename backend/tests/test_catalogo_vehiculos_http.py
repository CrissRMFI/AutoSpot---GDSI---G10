import uuid
from decimal import Decimal

from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _forzar_estado_vehiculo,
    _registrar_vehiculo,
    _registrar_y_loguear_usuario,
)
from app.models.documentacion_habilitante_conductor import DocumentacionHabilitanteConductor, EstadoHabilitacion
from app.models.reserva import Reserva
from sqlalchemy.orm import sessionmaker

from datetime import datetime, timedelta, timezone

def _aprobar_documentacion_conductor(engine, usuario_id: str):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        doc = DocumentacionHabilitanteConductor(
            usuario_id=uuid.UUID(usuario_id),
            estado_validacion=EstadoHabilitacion.APROBADO,
            categoria="B1",
            fecha_emision=datetime.now(timezone.utc).date() - timedelta(days=365),
            fecha_vencimiento=datetime.now(timezone.utc).date() + timedelta(days=365*4),
            foto_licencia_frente_url="http://example.com/frente.jpg",
            foto_licencia_dorso_url="http://example.com/dorso.jpg",
        )
        db.add(doc)
        db.commit()

def _crear_reserva_activa(engine, vehiculo_id: str, conductor_id: str):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        reserva = Reserva(
            vehiculo_id=uuid.UUID(vehiculo_id),
            conductor_id=uuid.UUID(conductor_id),
            codigo=f"AS-{uuid.uuid4().hex[:6].upper()}",
            estado="EN_CURSO",
            monto_total=Decimal("50000.00"),
            fecha_inicio=datetime.now(timezone.utc),
            fecha_fin=datetime.now(timezone.utc) + timedelta(days=2),
            estacion_retiro="Spot Almagro",
        )
        db.add(reserva)
        db.commit()

class TestCatalogoVehiculosHTTP:
    def test_catalogo_exito_con_documentacion_aprobada(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                # 1. Crear un vehículo habilitado y disponible
                vehiculo, prop_token = _registrar_vehiculo(client, "propietario@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "HABILITADO")
                client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(prop_token),
                )
                
                # Asignar un precio para que el filtro de precio > 0 se cumpla (requerido por listar_vehiculos_disponibles)
                client.patch(
                    f"/vehiculos/{vehiculo['id']}/precio",
                    json={"precio_por_dia": 50000},
                    headers=_auth_headers(prop_token),
                )

                # 2. Crear un cliente y aprobar su documentación
                cliente_id, token_cliente = _registrar_y_loguear_usuario(client, "cliente@autospot.com")
                _aprobar_documentacion_conductor(engine, cliente_id)

                # 3. Consultar catálogo
                response = client.get(
                    "/vehiculos/catalogo",
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 200
                data = response.json()
                assert len(data) >= 1
                assert any(v["id"] == vehiculo["id"] for v in data)
                
                # Verificar detalle del vehículo
                response_detalle = client.get(
                    f"/vehiculos/catalogo/{vehiculo['id']}",
                    headers=_auth_headers(token_cliente),
                )
                assert response_detalle.status_code == 200
                detalle = response_detalle.json()
                assert detalle["id"] == vehiculo["id"]
                assert detalle["marca"] == "Toyota"

        finally:
            from app.database import Base
            from app.main import app
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_catalogo_exito_sin_documentacion_aprobada(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, token_cliente = _registrar_y_loguear_usuario(client, "cliente_sin_doc@autospot.com")

                response = client.get(
                    "/vehiculos/catalogo",
                    headers=_auth_headers(token_cliente),
                )

                # Ahora el catálogo es público para cualquier usuario autenticado
                assert response.status_code == 200
                assert isinstance(response.json(), list)
                
                # El detalle de un vehículo inexistente debe fallar con 404 en lugar de 403
                response_detalle = client.get(
                    f"/vehiculos/catalogo/{uuid.uuid4()}",
                    headers=_auth_headers(token_cliente),
                )
                assert response_detalle.status_code == 404

        finally:
            from app.database import Base
            from app.main import app
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_catalogo_detalle_vehiculo_no_disponible(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                # 1. Crear vehículo pero NO ponerlo disponible
                vehiculo, prop_token = _registrar_vehiculo(client, "propietario@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "HABILITADO")
                # No actualizamos 'disponible' a True

                # 2. Cliente
                cliente_id, token_cliente = _registrar_y_loguear_usuario(client, "cliente2@autospot.com")
                _aprobar_documentacion_conductor(engine, cliente_id)

                # 3. Intentar acceder al detalle
                response_detalle = client.get(
                    f"/vehiculos/catalogo/{vehiculo['id']}",
                    headers=_auth_headers(token_cliente),
                )
                
                assert response_detalle.status_code == 404
                assert "no está disponible para alquiler" in response_detalle.text.lower()

        finally:
            from app.database import Base
            from app.main import app
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_catalogo_excluye_vehiculo_con_reserva_activa_aunque_este_disponible(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, prop_token = _registrar_vehiculo(client, "propietario@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "HABILITADO")
                client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(prop_token),
                )
                client.patch(
                    f"/vehiculos/{vehiculo['id']}/precio",
                    json={"precio_por_dia": 50000},
                    headers=_auth_headers(prop_token),
                )

                cliente_id, token_cliente = _registrar_y_loguear_usuario(
                    client, "cliente.reserva.activa@autospot.com"
                )
                _aprobar_documentacion_conductor(engine, cliente_id)
                _crear_reserva_activa(engine, vehiculo["id"], cliente_id)

                response = client.get(
                    "/vehiculos/catalogo",
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 200
                assert all(v["id"] != vehiculo["id"] for v in response.json())

                response_detalle = client.get(
                    f"/vehiculos/catalogo/{vehiculo['id']}",
                    headers=_auth_headers(token_cliente),
                )

                assert response_detalle.status_code == 404
                assert "no está disponible para alquiler" in response_detalle.text.lower()

        finally:
            from app.database import Base
            from app.main import app
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
