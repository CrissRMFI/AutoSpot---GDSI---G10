"""
Tests HTTP — Reportes de falla critica durante el alquiler.

Cubre el alta del reporte (validaciones de fotos, estado de reserva, duplicados),
las notificaciones a propietario y admins, el bloqueo de disponibilidad del
vehiculo y la resolucion del reporte (permisos y efecto sobre la disponibilidad).
"""
import uuid

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.reporte import Reporte
from app.models.reporte_foto import ReporteFoto
from app.models.reserva import Reserva
from app.models.vehiculo import Vehiculo
from tests.test_us7r8r_checkout_confirmacion_http import (
    _checkout_payload,
    _crear_alquiler_en_curso,
    _estado_reserva_y_disponibilidad,
    _notificaciones_por_tipo,
)
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _login_usuario,
    _registrar_y_loguear_usuario,
)


def _foto(orden: int = 1) -> dict:
    return {
        "url": f"https://res.cloudinary.com/demo/reporte-{orden}.jpg",
        "descripcion": f"Foto del problema {orden}",
        "formato": "jpg",
        "tamanio_bytes": 210000,
        "orden": orden,
    }


def _reporte_payload(cantidad_fotos: int = 1) -> dict:
    return {
        "descripcion": "El vehiculo no arranca luego de detenerlo.",
        "fotos": [_foto(i) for i in range(1, cantidad_fotos + 1)],
    }


def _token_propietario(client, sufijo: str) -> str:
    return _login_usuario(client, f"prop-{sufijo}@autospot.com")


def _datos_reserva(engine, reserva_id: str) -> tuple[str, str]:
    """Devuelve (conductor_id, vehiculo_id) de la reserva."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        reserva = db.query(Reserva).filter(Reserva.id == uuid.UUID(reserva_id)).first()
        return str(reserva.conductor_id), str(reserva.vehiculo_id)


def _insertar_reporte_activo(engine, reserva_id: str) -> str:
    """Inserta directamente un reporte ACTIVO con una foto para esa reserva."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        reserva = db.query(Reserva).filter(Reserva.id == uuid.UUID(reserva_id)).first()
        reporte = Reporte(
            reserva_id=reserva.id,
            conductor_id=reserva.conductor_id,
            vehiculo_id=reserva.vehiculo_id,
            descripcion="Falla critica inyectada",
            tipo="FALLA",
            criticidad="CRITICA",
            estado="ACTIVO",
        )
        reporte.fotos.append(
            ReporteFoto(
                url="https://res.cloudinary.com/demo/x.jpg",
                descripcion="evidencia",
                formato="jpg",
                tamanio_bytes=1000,
                orden=1,
            )
        )
        db.add(reporte)
        db.commit()
        return str(reporte.id)


class TestReportesCriticosHTTP:
    def _crear_reporte(self, client, engine, sufijo: str):
        reserva_id, token_cliente, token_admin = _crear_alquiler_en_curso(
            client, engine, sufijo
        )
        respuesta = client.post(
            f"/alquiler/reservas/{reserva_id}/reporte",
            json=_reporte_payload(1),
            headers=_auth_headers(token_cliente),
        )
        return reserva_id, token_cliente, token_admin, respuesta

    def test_crea_reporte_valido_una_foto(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, _, _, respuesta = self._crear_reporte(client, engine, "rep-ok1")
                assert respuesta.status_code == 201, respuesta.text
                body = respuesta.json()
                assert body["tipo"] == "FALLA"
                assert body["criticidad"] == "CRITICA"
                assert body["estado"] == "ACTIVO"
                assert len(body["fotos"]) == 1
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_crea_reporte_valido_diez_fotos(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _ = _crear_alquiler_en_curso(
                    client, engine, "rep-ok10"
                )
                respuesta = client.post(
                    f"/alquiler/reservas/{reserva_id}/reporte",
                    json=_reporte_payload(10),
                    headers=_auth_headers(token_cliente),
                )
                assert respuesta.status_code == 201, respuesta.text
                assert len(respuesta.json()["fotos"]) == 10
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechaza_reporte_sin_fotos(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _ = _crear_alquiler_en_curso(
                    client, engine, "rep-sinfotos"
                )
                respuesta = client.post(
                    f"/alquiler/reservas/{reserva_id}/reporte",
                    json={"descripcion": "falla", "fotos": []},
                    headers=_auth_headers(token_cliente),
                )
                assert respuesta.status_code == 422, respuesta.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechaza_reporte_mas_de_diez_fotos(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _ = _crear_alquiler_en_curso(
                    client, engine, "rep-11fotos"
                )
                respuesta = client.post(
                    f"/alquiler/reservas/{reserva_id}/reporte",
                    json=_reporte_payload(11),
                    headers=_auth_headers(token_cliente),
                )
                assert respuesta.status_code == 422, respuesta.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechaza_foto_sin_descripcion(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _ = _crear_alquiler_en_curso(
                    client, engine, "rep-sindesc"
                )
                payload = _reporte_payload(1)
                payload["fotos"][0]["descripcion"] = "   "
                respuesta = client.post(
                    f"/alquiler/reservas/{reserva_id}/reporte",
                    json=payload,
                    headers=_auth_headers(token_cliente),
                )
                assert respuesta.status_code == 422, respuesta.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechaza_reserva_inexistente(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, token_cliente, _ = _crear_alquiler_en_curso(
                    client, engine, "rep-inexistente"
                )
                respuesta = client.post(
                    f"/alquiler/reservas/{uuid.uuid4()}/reporte",
                    json=_reporte_payload(1),
                    headers=_auth_headers(token_cliente),
                )
                assert respuesta.status_code == 404, respuesta.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechaza_reserva_ajena(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, _, _ = _crear_alquiler_en_curso(client, engine, "rep-duenio")
                # Otro cliente distinto al conductor de la reserva.
                _, token_intruso = _registrar_y_loguear_usuario(
                    client, "intruso-rep@autospot.com"
                )
                respuesta = client.post(
                    f"/alquiler/reservas/{reserva_id}/reporte",
                    json=_reporte_payload(1),
                    headers=_auth_headers(token_intruso),
                )
                assert respuesta.status_code == 404, respuesta.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechaza_reserva_en_estado_no_permitido(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _ = _crear_alquiler_en_curso(
                    client, engine, "rep-estado"
                )
                # Forzar un estado no reportable.
                TestingSessionLocal = sessionmaker(
                    autocommit=False, autoflush=False, bind=engine
                )
                with TestingSessionLocal() as db:
                    reserva = (
                        db.query(Reserva)
                        .filter(Reserva.id == uuid.UUID(reserva_id))
                        .first()
                    )
                    reserva.estado = "FINALIZADA"
                    db.commit()
                respuesta = client.post(
                    f"/alquiler/reservas/{reserva_id}/reporte",
                    json=_reporte_payload(1),
                    headers=_auth_headers(token_cliente),
                )
                assert respuesta.status_code == 409, respuesta.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechaza_segundo_reporte_misma_reserva(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, primera = self._crear_reporte(
                    client, engine, "rep-dup"
                )
                assert primera.status_code == 201
                # Tras el primer reporte la reserva queda en INCIDENTE_REPORTADO;
                # forzamos EN_CURSO para que el rechazo sea por duplicado y no por estado.
                TestingSessionLocal = sessionmaker(
                    autocommit=False, autoflush=False, bind=engine
                )
                with TestingSessionLocal() as db:
                    reserva = (
                        db.query(Reserva)
                        .filter(Reserva.id == uuid.UUID(reserva_id))
                        .first()
                    )
                    reserva.estado = "EN_CURSO"
                    db.commit()
                segunda = client.post(
                    f"/alquiler/reservas/{reserva_id}/reporte",
                    json=_reporte_payload(1),
                    headers=_auth_headers(token_cliente),
                )
                assert segunda.status_code == 409, segunda.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_notifica_propietario_y_admins_y_cambia_estado_reserva(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, _, _, respuesta = self._crear_reporte(
                    client, engine, "rep-notif"
                )
                assert respuesta.status_code == 201, respuesta.text
                notifs = _notificaciones_por_tipo(engine, "REPORTE_FALLA_CRITICA")
                # Al menos propietario + un admin.
                assert len(notifs) >= 2
                estado, disponible = _estado_reserva_y_disponibilidad(engine, reserva_id)
                assert estado == "INCIDENTE_REPORTADO"
                assert disponible is False
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_checkout_con_reporte_activo_no_libera_disponibilidad(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, token_admin = _crear_alquiler_en_curso(
                    client, engine, "rep-checkout"
                )
                client.post(
                    f"/alquiler/reservas/{reserva_id}/entregar",
                    headers=_auth_headers(token_cliente),
                )
                client.post(
                    f"/alquiler/reservas/admin/{reserva_id}/registrar-entrada",
                    headers=_auth_headers(token_admin),
                )
                checkout = client.post(
                    "/checkouts",
                    json=_checkout_payload(reserva_id),
                    headers=_auth_headers(token_admin),
                ).json()
                # Reporte critico activo antes de confirmar el checkout.
                _insertar_reporte_activo(engine, reserva_id)
                confirmacion = client.post(
                    f"/alquiler/checkouts/{checkout['id']}/confirmar",
                    headers=_auth_headers(token_cliente),
                )
                assert confirmacion.status_code == 200, confirmacion.text
                estado, disponible = _estado_reserva_y_disponibilidad(engine, reserva_id)
                assert estado == "FINALIZADA"
                assert disponible is False
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_rechaza_marcar_disponible_con_reporte_activo(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, _, _, respuesta = self._crear_reporte(
                    client, engine, "rep-disp"
                )
                vehiculo_id = respuesta.json()["vehiculo_id"]
                token_prop = _token_propietario(client, "rep-disp")
                cambio = client.patch(
                    f"/vehiculos/{vehiculo_id}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token_prop),
                )
                assert cambio.status_code == 409, cambio.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_propietario_resuelve_reporte_propio(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, _, _, respuesta = self._crear_reporte(client, engine, "rep-prop")
                reporte_id = respuesta.json()["id"]
                token_prop = _token_propietario(client, "rep-prop")
                resolucion = client.post(
                    f"/reportes/{reporte_id}/resolver",
                    json={"resolucion_descripcion": "Se coordino asistencia tecnica."},
                    headers=_auth_headers(token_prop),
                )
                assert resolucion.status_code == 200, resolucion.text
                assert resolucion.json()["estado"] == "RESUELTO"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_admin_resuelve_reporte(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, _, token_admin, respuesta = self._crear_reporte(
                    client, engine, "rep-admin"
                )
                reporte_id = respuesta.json()["id"]
                resolucion = client.post(
                    f"/reportes/{reporte_id}/resolver",
                    json={"resolucion_descripcion": "Caso revisado por administracion."},
                    headers=_auth_headers(token_admin),
                )
                assert resolucion.status_code == 200, resolucion.text
                assert resolucion.json()["estado"] == "RESUELTO"
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_cliente_no_puede_resolver_reporte(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, token_cliente, _, respuesta = self._crear_reporte(
                    client, engine, "rep-cli"
                )
                reporte_id = respuesta.json()["id"]
                resolucion = client.post(
                    f"/reportes/{reporte_id}/resolver",
                    json={"resolucion_descripcion": "No deberia poder."},
                    headers=_auth_headers(token_cliente),
                )
                assert resolucion.status_code == 403, resolucion.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_resolver_reporte_no_cambia_disponibilidad(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, _, token_admin, respuesta = self._crear_reporte(
                    client, engine, "rep-noflip"
                )
                reporte_id = respuesta.json()["id"]
                resolucion = client.post(
                    f"/reportes/{reporte_id}/resolver",
                    json={"resolucion_descripcion": "Resuelto sin republicar."},
                    headers=_auth_headers(token_admin),
                )
                assert resolucion.status_code == 200, resolucion.text
                _, disponible = _estado_reserva_y_disponibilidad(engine, reserva_id)
                assert disponible is False
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_upload_foto_reporte_rechaza_formato_invalido(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, token_cliente, _ = _crear_alquiler_en_curso(
                    client, engine, "rep-upload"
                )
                respuesta = client.post(
                    "/upload/foto-reporte",
                    files={"archivo": ("nota.txt", b"contenido", "text/plain")},
                    headers=_auth_headers(token_cliente),
                )
                assert respuesta.status_code == 400, respuesta.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
