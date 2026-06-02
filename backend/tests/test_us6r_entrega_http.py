"""
Tests HTTP para US 6R: Entrega (Registrar salida de vehículo).
"""
import uuid
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.reserva import Reserva
from app.models.notificacion import Notificacion

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
from tests.test_us5r_verificar_codigo_reserva_http import (
    _registrar_datos_personales_directo,
)


def _payload_checkin(reserva_id: str) -> dict:
    return {
        "reserva_id": reserva_id,
        "nivel_combustible": "Lleno",
        "kilometraje_actual": 12000,
        "esta_limpio": True,
        "tiene_danios": False,
        "url_foto_frente": "frente.jpg",
        "url_foto_trasera": "trasera.jpg",
        "url_foto_lateral_izq": "izq.jpg",
        "url_foto_lateral_der": "der.jpg",
        "url_foto_panel": "panel.jpg",
        "urls_fotos_danios": []
    }


def _notificaciones_por_tipo(engine, tipo: str) -> list[Notificacion]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        return db.query(Notificacion).filter(Notificacion.tipo == tipo).all()


def _crear_reserva_con_estado(client, engine, sufijo: str, verificar: bool = False):
    _registrar_admin_directo(engine, email=f"admin-{sufijo}@autospot.com")
    token_admin = _login_usuario(client, f"admin-{sufijo}@autospot.com")
    
    vehiculo, _ = _registrar_vehiculo(client, f"prop-{sufijo}@autospot.com")
    _hacer_vehiculo_reservable(engine, vehiculo["id"])
    
    conductor_id, token_cliente = _registrar_y_loguear_usuario(
        client,
        f"cliente-{sufijo}@autospot.com",
    )
    _registrar_datos_personales_directo(engine, conductor_id)

    creacion = client.post(
        "/alquiler/reservas",
        json=_payload_reserva(vehiculo["id"]),
        headers=_auth_headers(token_cliente),
    )
    reserva = creacion.json()

    if verificar:
        client.post(
            "/alquiler/reservas/verificar-codigo",
            json={"codigo_reserva": reserva["codigo_reserva"]},
            headers=_auth_headers(token_admin),
        )

    return reserva["id"], token_cliente, token_admin


class TestUS6REntregaHTTP:
    def test_ca3_registrar_salida_sin_verificar_codigo_devuelve_error(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, _, token_admin = _crear_reserva_con_estado(
                    client, engine, "ca3", verificar=False
                )

                salida = client.post(
                    f"/alquiler/reservas/admin/{reserva_id}/salida",
                    headers=_auth_headers(token_admin),
                )

                assert salida.status_code in [400, 409]
                assert "verificar" in salida.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ca1_registrar_salida_sin_checkin_devuelve_error(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, _, token_admin = _crear_reserva_con_estado(
                    client, engine, "ca1", verificar=True
                )

                salida = client.post(
                    f"/alquiler/reservas/admin/{reserva_id}/salida",
                    headers=_auth_headers(token_admin),
                )

                assert salida.status_code in [400, 409]
                assert "check-in" in salida.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ca4_ca2_registrar_salida_con_checkin_valido_inicia_alquiler_y_notifica(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, token_admin = _crear_reserva_con_estado(
                    client, engine, "ca4", verificar=True
                )

                checkin_res = client.post(
                    "/checkins",
                    json=_payload_checkin(reserva_id),
                    headers=_auth_headers(token_cliente),
                )
                assert checkin_res.status_code == 201

                checkin_id = checkin_res.json()["id"]
                client.post(
                    f"/admin/checkins/{checkin_id}/aprobar",
                    headers=_auth_headers(token_admin),
                )

                salida = client.post(
                    f"/alquiler/reservas/admin/{reserva_id}/salida",
                    headers=_auth_headers(token_admin),
                )

                assert salida.status_code == 200, salida.text
                salida_body = salida.json()
                assert salida_body["estado"] == "EN_CURSO"
                assert salida_body["fecha_salida_real"] is not None

                notificaciones = _notificaciones_por_tipo(engine, "ALQUILER_INICIADO")
                assert len(notificaciones) > 0
                assert any(str(reserva_id) == str(n.recurso_id) for n in notificaciones if n.recurso_id)

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ca6_rechazar_checkin_requiere_motivo(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, token_admin = _crear_reserva_con_estado(
                    client, engine, "ca6", verificar=True
                )

                checkin_res = client.post(
                    "/checkins",
                    json=_payload_checkin(reserva_id),
                    headers=_auth_headers(token_cliente),
                )
                checkin_id = checkin_res.json()["id"]

                rechazo_sin_motivo = client.post(
                    f"/admin/checkins/{checkin_id}/rechazo",
                    json={},  # Sin motivo
                    headers=_auth_headers(token_admin),
                )
                assert rechazo_sin_motivo.status_code == 422

                rechazo_con_motivo = client.post(
                    f"/admin/checkins/{checkin_id}/rechazo",
                    json={"motivo": "Falta foto clara del lateral derecho."},
                    headers=_auth_headers(token_admin),
                )
                assert rechazo_con_motivo.status_code == 200
                assert rechazo_con_motivo.json()["estado"] == "RECHAZADO"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ca5_registrar_salida_con_checkin_rechazado_devuelve_error(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, token_admin = _crear_reserva_con_estado(
                    client, engine, "ca5", verificar=True
                )

                checkin_res = client.post(
                    "/checkins",
                    json=_payload_checkin(reserva_id),
                    headers=_auth_headers(token_cliente),
                )
                checkin_id = checkin_res.json()["id"]

                client.post(
                    f"/admin/checkins/{checkin_id}/rechazo",
                    json={"motivo": "Foto borrosa"},
                    headers=_auth_headers(token_admin),
                )

                salida = client.post(
                    f"/alquiler/reservas/admin/{reserva_id}/salida",
                    headers=_auth_headers(token_admin),
                )

                assert salida.status_code in [400, 409]
                assert "reenviar" in salida.json()["detail"].lower() or "rechazado" in salida.json()["detail"].lower()

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
