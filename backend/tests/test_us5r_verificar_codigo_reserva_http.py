"""
Tests HTTP — US 5R: Verificar código de reserva.
"""
import uuid

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.models.notificacion import Notificacion
from app.models.vehiculo import Vehiculo
from tests.test_us14c_obtener_codigo_reserva_http import (
    _hacer_vehiculo_reservable,
    _payload_reserva,
    _registrar_admin_directo,
)
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _login_usuario,
    _registrar_vehiculo,
    _registrar_y_loguear_usuario,
)


def _registrar_datos_personales_directo(engine, usuario_id: str) -> None:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        datos = DatosPersonalesUsuario(
            usuario_id=uuid.UUID(usuario_id),
            dni="30111222",
            nombre="Carla",
            apellido="Reserva",
            foto_dni_frente_url="uploads/dni/30111222/frente.jpg",
            foto_dni_dorso_url="uploads/dni/30111222/dorso.jpg",
            estado_validacion="APROBADO",
        )
        db.add(datos)
        db.commit()


def _notificaciones_reserva_pendientes(engine) -> list[Notificacion]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        return (
            db.query(Notificacion)
            .filter(
                Notificacion.tipo == "RESERVA_PENDIENTE_VERIFICACION",
                Notificacion.vista_at.is_(None),
            )
            .all()
        )


class TestUS5RVerificarCodigoReservaHTTP:
    def test_reserva_crea_notificacion_admin_y_verificacion_la_resuelve(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(engine, email="admin5r@autospot.com")
                token_admin = _login_usuario(client, "admin5r@autospot.com")
                vehiculo, _ = _registrar_vehiculo(client, "prop5r@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                conductor_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente5r@autospot.com",
                )
                _registrar_datos_personales_directo(engine, conductor_id)

                creacion = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )

                assert creacion.status_code == 201, creacion.text
                reserva = creacion.json()
                notificaciones = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token_admin),
                )

                assert notificaciones.status_code == 200
                pendientes = [
                    item for item in notificaciones.json()
                    if item["tipo"] == "RESERVA_PENDIENTE_VERIFICACION"
                ]
                assert len(pendientes) == 1
                assert pendientes[0]["recurso_id"] == reserva["id"]

                detalle = client.get(
                    f"/alquiler/reservas/admin/{reserva['id']}",
                    headers=_auth_headers(token_admin),
                )

                assert detalle.status_code == 200, detalle.text
                body_detalle = detalle.json()
                assert body_detalle["codigo_reserva"] == reserva["codigo_reserva"]
                assert body_detalle["conductor"]["nombre"] == "Carla"
                assert body_detalle["conductor"]["apellido"] == "Reserva"
                assert body_detalle["conductor"]["dni"] == "30111222"
                assert body_detalle["vehiculo"]["patente"] == "AB123CD"
                assert body_detalle["puede_entregar"] is False

                verificacion = client.post(
                    "/alquiler/reservas/verificar-codigo",
                    json={"codigo_reserva": reserva["codigo_reserva"]},
                    headers=_auth_headers(token_admin),
                )

                assert verificacion.status_code == 200, verificacion.text
                body_verificacion = verificacion.json()
                assert body_verificacion["codigo_verificado_at"] is not None
                assert body_verificacion["estado"] == "VERIFICADA"
                assert body_verificacion["puede_entregar"] is True
                assert _notificaciones_reserva_pendientes(engine) == []

                notif_cliente = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token_cliente),
                )
                assert notif_cliente.status_code == 200
                aprobadas = [
                    item for item in notif_cliente.json()
                    if item["tipo"] == "RESERVA_APROBADA"
                ]
                assert len(aprobadas) == 1
                assert aprobadas[0]["recurso_id"] == reserva["id"]
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechazar_reserva_libera_vehiculo_y_notifica_al_cliente(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(engine, email="admin5r-rechazo@autospot.com")
                token_admin = _login_usuario(client, "admin5r-rechazo@autospot.com")
                vehiculo, _ = _registrar_vehiculo(client, "prop5r-rechazo@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                conductor_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente5r-rechazo@autospot.com",
                )
                _registrar_datos_personales_directo(engine, conductor_id)

                creacion = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )
                assert creacion.status_code == 201, creacion.text
                reserva = creacion.json()

                rechazo = client.post(
                    f"/alquiler/reservas/admin/{reserva['id']}/rechazar",
                    json={"motivo": "El DNI presentado no coincide."},
                    headers=_auth_headers(token_admin),
                )

                assert rechazo.status_code == 200, rechazo.text
                body_rechazo = rechazo.json()
                assert body_rechazo["estado"] == "RECHAZADA"
                assert body_rechazo["motivo_rechazo"] == "El DNI presentado no coincide."
                assert body_rechazo["puede_entregar"] is False

                TestingSessionLocal = sessionmaker(
                    autocommit=False, autoflush=False, bind=engine,
                )
                with TestingSessionLocal() as db:
                    veh = db.query(Vehiculo).filter(
                        Vehiculo.id == uuid.UUID(vehiculo["id"])
                    ).first()
                    assert veh.disponible is True

                assert _notificaciones_reserva_pendientes(engine) == []

                notif_cliente = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token_cliente),
                )
                assert notif_cliente.status_code == 200
                rechazadas = [
                    item for item in notif_cliente.json()
                    if item["tipo"] == "RESERVA_RECHAZADA"
                ]
                assert len(rechazadas) == 1
                assert rechazadas[0]["recurso_id"] == reserva["id"]
                assert "DNI presentado" in rechazadas[0]["mensaje"]
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechazar_reserva_ya_verificada_devuelve_409(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(engine, email="admin5r-r2@autospot.com")
                token_admin = _login_usuario(client, "admin5r-r2@autospot.com")
                vehiculo, _ = _registrar_vehiculo(client, "prop5r-r2@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                conductor_id, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente5r-r2@autospot.com",
                )
                _registrar_datos_personales_directo(engine, conductor_id)

                creacion = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )
                reserva = creacion.json()

                client.post(
                    "/alquiler/reservas/verificar-codigo",
                    json={"codigo_reserva": reserva["codigo_reserva"]},
                    headers=_auth_headers(token_admin),
                )

                rechazo = client.post(
                    f"/alquiler/reservas/admin/{reserva['id']}/rechazar",
                    json={"motivo": "Llegó tarde."},
                    headers=_auth_headers(token_admin),
                )

                assert rechazo.status_code == 409
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechazar_reserva_sin_motivo_devuelve_422(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(engine, email="admin5r-r3@autospot.com")
                token_admin = _login_usuario(client, "admin5r-r3@autospot.com")
                vehiculo, _ = _registrar_vehiculo(client, "prop5r-r3@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])
                _, token_cliente = _registrar_y_loguear_usuario(
                    client,
                    "cliente5r-r3@autospot.com",
                )

                creacion = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )
                reserva = creacion.json()

                rechazo = client.post(
                    f"/alquiler/reservas/admin/{reserva['id']}/rechazar",
                    json={"motivo": "   "},
                    headers=_auth_headers(token_admin),
                )

                assert rechazo.status_code == 422
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
