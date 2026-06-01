"""
Tests HTTP para US 7R / 8R: recepción, checkout y confirmación del cliente.
"""
from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.checkout_vehiculo import CheckoutVehiculo
from app.models.notificacion import Notificacion
from app.models.reserva import Reserva
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


def _checkout_payload(reserva_id: str) -> dict:
    return {
        "reserva_id": reserva_id,
        "nivel_combustible": "Lleno",
        "kilometraje_actual": 24000,
        "esta_limpio": True,
        "tiene_danios": False,
        "descripcion_danios": None,
        "url_foto_frente": "uploads/checkout/frente.jpg",
        "url_foto_trasera": "uploads/checkout/trasera.jpg",
        "url_foto_lateral_izq": "uploads/checkout/izq.jpg",
        "url_foto_lateral_der": "uploads/checkout/der.jpg",
        "url_foto_panel": "uploads/checkout/panel.jpg",
        "urls_fotos_danios": [],
        "url_foto_extra": None,
        "notas_adicionales": "Sin novedades.",
    }


def _forzar_reserva_en_curso(engine, reserva_id: str) -> None:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    ahora = datetime.now(timezone.utc)
    with TestingSessionLocal() as db:
        reserva = db.query(Reserva).filter(Reserva.id == uuid.UUID(reserva_id)).first()
        reserva.estado = "EN_CURSO"
        reserva.codigo_verificado_at = ahora - timedelta(days=2)
        reserva.fecha_inicio = ahora - timedelta(days=2)
        reserva.fecha_fin = ahora + timedelta(hours=3)
        reserva.fecha_salida_real = ahora - timedelta(days=2)
        db.commit()


def _estado_reserva_y_disponibilidad(engine, reserva_id: str) -> tuple[str, bool]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        reserva = db.query(Reserva).filter(Reserva.id == uuid.UUID(reserva_id)).first()
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == reserva.vehiculo_id).first()
        return reserva.estado, vehiculo.disponible


def _notificaciones_por_tipo(engine, tipo: str) -> list[Notificacion]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        return db.query(Notificacion).filter(Notificacion.tipo == tipo).all()


def _cantidad_checkouts(engine, reserva_id: str) -> int:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        return (
            db.query(CheckoutVehiculo)
            .filter(CheckoutVehiculo.reserva_id == uuid.UUID(reserva_id))
            .count()
        )


def _crear_alquiler_en_curso(client, engine, sufijo: str):
    _registrar_admin_directo(engine, email=f"admin-{sufijo}@autospot.com")
    token_admin = _login_usuario(client, f"admin-{sufijo}@autospot.com")
    vehiculo, _ = _registrar_vehiculo(client, f"prop-{sufijo}@autospot.com")
    _hacer_vehiculo_reservable(engine, vehiculo["id"])
    _, token_cliente = _registrar_y_loguear_usuario(
        client,
        f"cliente-{sufijo}@autospot.com",
    )

    creacion = client.post(
        "/alquiler/reservas",
        json=_payload_reserva(vehiculo["id"]),
        headers=_auth_headers(token_cliente),
    )
    assert creacion.status_code == 201, creacion.text
    reserva_id = creacion.json()["id"]
    _forzar_reserva_en_curso(engine, reserva_id)
    return reserva_id, token_cliente, token_admin


class TestUS7R8RCheckoutConfirmacionHTTP:
    def test_cliente_entrega_admin_checkout_y_cliente_confirma(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, token_admin = _crear_alquiler_en_curso(
                    client,
                    engine,
                    "flujo-ok",
                )

                entrega = client.post(
                    f"/alquiler/reservas/{reserva_id}/entregar",
                    headers=_auth_headers(token_cliente),
                )

                assert entrega.status_code == 200, entrega.text
                assert entrega.json()["estado"] == "ENTREGA_SOLICITADA"
                assert entrega.json()["fecha_entrega_solicitada"] is not None
                assert _notificaciones_por_tipo(engine, "AUTO_DEVUELTO")

                recepcion = client.get(
                    "/alquiler/reservas/admin/recepcion?page=1&size=10",
                    headers=_auth_headers(token_admin),
                )
                assert recepcion.status_code == 200, recepcion.text
                assert recepcion.json()["items"][0]["id"] == reserva_id
                assert recepcion.json()["items"][0]["estado"] == "ENTREGA_SOLICITADA"

                checkout_temprano = client.post(
                    "/checkouts",
                    json=_checkout_payload(reserva_id),
                    headers=_auth_headers(token_admin),
                )
                assert checkout_temprano.status_code == 400

                entrada = client.post(
                    f"/alquiler/reservas/admin/{reserva_id}/registrar-entrada",
                    headers=_auth_headers(token_admin),
                )
                assert entrada.status_code == 200, entrada.text
                assert entrada.json()["estado"] == "DEVUELTO"
                assert entrada.json()["fecha_devolucion_real"] is not None

                checkout = client.post(
                    "/checkouts",
                    json=_checkout_payload(reserva_id),
                    headers=_auth_headers(token_admin),
                )

                assert checkout.status_code == 201, checkout.text
                checkout_body = checkout.json()
                assert checkout_body["estado"] == "PENDIENTE_CONFIRMACION"
                assert _estado_reserva_y_disponibilidad(engine, reserva_id) == (
                    "CHECKOUT_PENDIENTE",
                    False,
                )

                notificaciones_cliente = client.get(
                    "/notificaciones",
                    headers=_auth_headers(token_cliente),
                )
                tipos_cliente = {item["tipo"] for item in notificaciones_cliente.json()}
                assert "CHECKOUT_PENDIENTE_CONFIRMACION" in tipos_cliente

                mis_alquileres = client.get(
                    "/alquiler/mis-alquileres",
                    headers=_auth_headers(token_cliente),
                )
                assert mis_alquileres.status_code == 200
                assert mis_alquileres.json()["items"][0]["estado"] == "CHECKOUT_PENDIENTE"

                confirmacion = client.post(
                    f"/alquiler/checkouts/{checkout_body['id']}/confirmar",
                    headers=_auth_headers(token_cliente),
                )

                assert confirmacion.status_code == 200, confirmacion.text
                assert confirmacion.json()["estado"] == "CONFIRMADO"
                assert _estado_reserva_y_disponibilidad(engine, reserva_id) == (
                    "FINALIZADA",
                    True,
                )
                assert _notificaciones_por_tipo(engine, "CHECKOUT_CONFIRMADO")
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_cliente_rechaza_y_admin_reenvia_checkout_con_historial(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, token_admin = _crear_alquiler_en_curso(
                    client,
                    engine,
                    "flujo-rechazo",
                )
                client.post(
                    f"/alquiler/reservas/{reserva_id}/entregar",
                    headers=_auth_headers(token_cliente),
                )
                entrada = client.post(
                    f"/alquiler/reservas/admin/{reserva_id}/registrar-entrada",
                    headers=_auth_headers(token_admin),
                )
                assert entrada.status_code == 200, entrada.text
                primer_checkout = client.post(
                    "/checkouts",
                    json=_checkout_payload(reserva_id),
                    headers=_auth_headers(token_admin),
                ).json()

                rechazo = client.post(
                    f"/alquiler/checkouts/{primer_checkout['id']}/rechazar",
                    json={"motivo": "El kilometraje informado no coincide."},
                    headers=_auth_headers(token_cliente),
                )

                assert rechazo.status_code == 200, rechazo.text
                assert rechazo.json()["estado"] == "RECHAZADO"
                assert rechazo.json()["motivo_rechazo"] == "El kilometraje informado no coincide."
                assert _estado_reserva_y_disponibilidad(engine, reserva_id) == (
                    "DEVUELTO",
                    False,
                )
                assert _notificaciones_por_tipo(engine, "CHECKOUT_RECHAZADO")

                segundo_checkout = client.post(
                    "/checkouts",
                    json={**_checkout_payload(reserva_id), "kilometraje_actual": 24015},
                    headers=_auth_headers(token_admin),
                )

                assert segundo_checkout.status_code == 201, segundo_checkout.text
                assert segundo_checkout.json()["id"] != primer_checkout["id"]
                assert segundo_checkout.json()["estado"] == "PENDIENTE_CONFIRMACION"
                assert _cantidad_checkouts(engine, reserva_id) == 2
                assert _estado_reserva_y_disponibilidad(engine, reserva_id) == (
                    "CHECKOUT_PENDIENTE",
                    False,
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
