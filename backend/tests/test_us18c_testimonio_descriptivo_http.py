"""
Tests HTTP — US 18C: Testimonio descriptivo de la experiencia.

Metodología TDD — Fase RED:
    Estos tests DEBEN FALLAR porque el endpoint, el modelo ORM y el servicio
    de testimonios aún no existen.

Criterios de Aceptación cubiertos:

    CA 1 — Al registrar un testimonio sobre una reserva FINALIZADA, el sistema
            lo vincula de forma permanente al identificador del viaje y al
            vehículo asociado.

    CA 2 — El testimonio queda integrado al histórico público del vehículo,
            permitiendo que futuros conductores lo consulten mediante el
            endpoint de lectura.

    CA 3 — El sistema garantiza la inmutabilidad: rechaza con 409 cualquier
            intento de registrar un segundo testimonio sobre la misma reserva,
            y devuelve 405 (Method Not Allowed) ante cualquier intento de
            modificar (PUT/PATCH) un testimonio existente.

Nota sobre el campo `descripcion`:
    El campo es OPCIONAL. El conductor puede registrar un testimonio sin texto
    (descripcion=None o descripcion omitida) y el sistema debe aceptarlo con 201.
"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.reserva import Reserva

# Reutilizamos helpers ya existentes de otros test suites para construir
# el estado de la base de datos necesario (propietario, vehículo, conductor,
# reserva finalizada).
from tests.test_us14c_obtener_codigo_reserva_http import (
    _hacer_vehiculo_reservable,
    _payload_reserva,
)
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _registrar_vehiculo,
    _registrar_y_loguear_usuario,
)


# ── Helpers internos ──────────────────────────────────────────────────────────

def _forzar_reserva_finalizada(engine, reserva_id: str) -> None:
    """
    Mueve la reserva indicada al estado FINALIZADA con devolución física
    registrada, simulando el flujo completo (checkin → en_curso → devuelto
    → checkout confirmado → finalizada).
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    ahora = datetime.now(timezone.utc)
    with TestingSessionLocal() as db:
        reserva = db.query(Reserva).filter(
            Reserva.id == uuid.UUID(reserva_id)
        ).first()
        reserva.estado = "FINALIZADA"
        reserva.codigo_verificado_at = ahora - timedelta(days=5)
        reserva.fecha_inicio = ahora - timedelta(days=5)
        reserva.fecha_fin = ahora - timedelta(days=2)
        reserva.fecha_salida_real = ahora - timedelta(days=5)
        reserva.fecha_devolucion_real = ahora - timedelta(days=2)
        db.commit()


def _crear_reserva_finalizada(client, engine, sufijo: str):
    """
    Construye el escenario completo:
      propietario → vehículo → conductor → reserva → forzar FINALIZADA.

    Devuelve (reserva_id, token_conductor, vehiculo_id).
    """
    propietario_email = f"prop-ts-{sufijo}@autospot.com"
    vehiculo, _ = _registrar_vehiculo(client, propietario_email)
    _hacer_vehiculo_reservable(engine, vehiculo["id"])

    _, token_conductor = _registrar_y_loguear_usuario(
        client, f"conductor-ts-{sufijo}@autospot.com"
    )

    resp_reserva = client.post(
        "/alquiler/reservas",
        json=_payload_reserva(vehiculo["id"]),
        headers=_auth_headers(token_conductor),
    )
    assert resp_reserva.status_code == 201, resp_reserva.text
    reserva_id = resp_reserva.json()["id"]

    _forzar_reserva_finalizada(engine, reserva_id)

    return reserva_id, token_conductor, vehiculo["id"]


# ═════════════════════════════════════════════════════════════════════════════
#  CA 1 — Creación vinculada al viaje y al vehículo
# ═════════════════════════════════════════════════════════════════════════════

class TestCA1_CreacionTestimonio:
    """
    CA 1: Al suministrar una descripción sobre una reserva finalizada,
    el sistema debe vincular el relato de forma permanente al viaje y al
    vehículo correspondiente.
    """

    def test_crear_testimonio_con_descripcion_devuelve_201(self):
        """
        Dado: una reserva FINALIZADA.
        Cuando: el conductor POST /testimonios con un texto de descripción.
        Entonces: el sistema responde 201 con el testimonio creado,
                  incluyendo reserva_id y vehiculo_id correctos.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, vehiculo_id = (
                    _crear_reserva_finalizada(client, engine, "ca1-con-texto")
                )

                response = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": "Excelente vehículo, muy puntual y limpio.",
                    },
                    headers=_auth_headers(token_conductor),
                )

                assert response.status_code == 201, (
                    f"Se esperaba 201, se recibió {response.status_code}: {response.text}"
                )
                body = response.json()
                assert body["reserva_id"] == reserva_id, (
                    "El testimonio debe estar vinculado al reserva_id correcto."
                )
                assert body["vehiculo_id"] == vehiculo_id, (
                    "El testimonio debe estar vinculado al vehiculo_id correcto."
                )
                assert body["descripcion"] == "Excelente vehículo, muy puntual y limpio."
                assert "conductor_id" in body
                assert "id" in body
                assert "created_at" in body
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_crear_testimonio_sin_descripcion_devuelve_201(self):
        """
        Dado: una reserva FINALIZADA.
        Cuando: el conductor POST /testimonios sin enviar el campo descripcion.
        Entonces: el sistema responde 201 (el campo es opcional).

        Requisito Frontend: el textarea NO debe ser obligatorio para enviar el formulario.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, vehiculo_id = (
                    _crear_reserva_finalizada(client, engine, "ca1-sin-texto")
                )

                response = client.post(
                    "/testimonios",
                    json={"reserva_id": reserva_id},  # descripcion omitida
                    headers=_auth_headers(token_conductor),
                )

                assert response.status_code == 201, (
                    f"Testimonio sin descripción debería ser aceptado con 201, "
                    f"se recibió {response.status_code}: {response.text}"
                )
                body = response.json()
                assert body["reserva_id"] == reserva_id
                assert body["vehiculo_id"] == vehiculo_id
                assert body["descripcion"] is None
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_crear_testimonio_descripcion_nula_explicita_devuelve_201(self):
        """
        Dado: una reserva FINALIZADA.
        Cuando: el conductor envía descripcion=null explícitamente.
        Entonces: el sistema responde 201 (null es un valor válido para el campo opcional).
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, _ = (
                    _crear_reserva_finalizada(client, engine, "ca1-null")
                )

                response = client.post(
                    "/testimonios",
                    json={"reserva_id": reserva_id, "descripcion": None},
                    headers=_auth_headers(token_conductor),
                )

                assert response.status_code == 201, (
                    f"descripcion=null debería devolver 201, "
                    f"se recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_reserva_no_finalizada_rechaza_testimonio_con_400(self):
        """
        Dado: una reserva en estado CONFIRMADA (no finalizada).
        Cuando: el conductor intenta dejar un testimonio.
        Entonces: el sistema rechaza con 400 Bad Request.

        Solo se puede dejar testimonio sobre una contratación cerrada
        administrativamente (CA 1).
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_email = "prop-ts-nofin@autospot.com"
                vehiculo, _ = _registrar_vehiculo(client, propietario_email)
                _hacer_vehiculo_reservable(engine, vehiculo["id"])

                _, token_conductor = _registrar_y_loguear_usuario(
                    client, "conductor-ts-nofin@autospot.com"
                )
                resp = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_conductor),
                )
                assert resp.status_code == 201, resp.text
                reserva_id = resp.json()["id"]
                # La reserva queda en estado CONFIRMADA (sin forzar FINALIZADA)

                response = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": "Intento prematuro.",
                    },
                    headers=_auth_headers(token_conductor),
                )

                assert response.status_code == 400, (
                    f"Reserva no finalizada debería devolver 400, "
                    f"se recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_reserva_inexistente_devuelve_404(self):
        """
        Dado: un reserva_id que no existe en la base de datos.
        Cuando: el conductor intenta crear un testimonio.
        Entonces: el sistema devuelve 404 Not Found.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, token_conductor = _registrar_y_loguear_usuario(
                    client, "conductor-ts-404@autospot.com"
                )
                reserva_id_falso = str(uuid.uuid4())

                response = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id_falso,
                        "descripcion": "Reserva que no existe.",
                    },
                    headers=_auth_headers(token_conductor),
                )

                assert response.status_code == 404, (
                    f"Reserva inexistente debería devolver 404, "
                    f"se recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_descripcion_excede_1000_caracteres_devuelve_422(self):
        """
        Dado: una reserva FINALIZADA.
        Cuando: el conductor envía una descripción de más de 1000 caracteres.
        Entonces: Pydantic rechaza con 422 Unprocessable Entity.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, _ = (
                    _crear_reserva_finalizada(client, engine, "ca1-largo")
                )

                descripcion_larga = "x" * 2001

                response = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": descripcion_larga,
                    },
                    headers=_auth_headers(token_conductor),
                )

                assert response.status_code == 422, (
                    f"Descripción > 1000 chars debería devolver 422, "
                    f"se recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_endpoint_requiere_autenticacion(self):
        """
        Cuando: se hace POST /testimonios sin token de autenticación.
        Entonces: el sistema devuelve 401 Unauthorized.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                response = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": str(uuid.uuid4()),
                        "descripcion": "Sin token.",
                    },
                    # Sin headers de autorización
                )

                assert response.status_code == 401, (
                    f"Sin autenticación debería devolver 401, "
                    f"se recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ═════════════════════════════════════════════════════════════════════════════
#  CA 2 — Consulta del histórico público del vehículo
# ═════════════════════════════════════════════════════════════════════════════

class TestCA2_HistoricoPublico:
    """
    CA 2: Tras registrar un testimonio, debe ser consultable mediante el
    histórico público del vehículo para que futuros conductores puedan
    acceder a la información de confianza.
    """

    def test_testimonio_aparece_en_historico_del_vehiculo(self):
        """
        Dado: un testimonio creado para una reserva finalizada de un vehículo.
        Cuando: se consulta GET /vehiculos/{vehiculo_id}/testimonios.
        Entonces: el testimonio aparece en la respuesta pública.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, vehiculo_id = (
                    _crear_reserva_finalizada(client, engine, "ca2-hist")
                )

                # Registrar el testimonio
                post_resp = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": "Muy buena experiencia, lo recomiendo.",
                    },
                    headers=_auth_headers(token_conductor),
                )
                assert post_resp.status_code == 201, post_resp.text
                testimonio_id = post_resp.json()["id"]

                # Consultar el histórico público del vehículo
                get_resp = client.get(f"/vehiculos/{vehiculo_id}/testimonios")

                assert get_resp.status_code == 200, (
                    f"El histórico del vehículo debería devolver 200, "
                    f"se recibió {get_resp.status_code}: {get_resp.text}"
                )
                historico = get_resp.json()
                assert isinstance(historico, list), (
                    "El histórico debe ser una lista de testimonios."
                )
                ids_en_historico = [t["id"] for t in historico]
                assert testimonio_id in ids_en_historico, (
                    f"El testimonio {testimonio_id} no aparece en el histórico del vehículo."
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_historico_vacio_cuando_no_hay_testimonios(self):
        """
        Dado: un vehículo sin testimonios registrados.
        Cuando: se consulta GET /vehiculos/{vehiculo_id}/testimonios.
        Entonces: el sistema devuelve 200 con lista vacía (no 404).
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_email = "prop-ts-hist-vacio@autospot.com"
                vehiculo, _ = _registrar_vehiculo(client, propietario_email)
                vehiculo_id = vehiculo["id"]

                get_resp = client.get(f"/vehiculos/{vehiculo_id}/testimonios")

                assert get_resp.status_code == 200, (
                    f"Vehículo sin testimonios debería devolver 200 (lista vacía), "
                    f"se recibió {get_resp.status_code}: {get_resp.text}"
                )
                assert get_resp.json() == [], (
                    "La respuesta debería ser una lista vacía []."
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_historico_es_publico_sin_autenticacion(self):
        """
        Dado: un testimonio registrado.
        Cuando: un visitante no autenticado consulta el histórico del vehículo.
        Entonces: puede ver los testimonios (endpoint público, sin token).
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, vehiculo_id = (
                    _crear_reserva_finalizada(client, engine, "ca2-pub")
                )

                # Registrar con autenticación
                post_resp = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": "Cómodo y económico.",
                    },
                    headers=_auth_headers(token_conductor),
                )
                assert post_resp.status_code == 201, post_resp.text

                # Consultar SIN token
                get_resp = client.get(f"/vehiculos/{vehiculo_id}/testimonios")

                assert get_resp.status_code == 200, (
                    f"El histórico público no debería requerir autenticación, "
                    f"se recibió {get_resp.status_code}: {get_resp.text}"
                )
                historico = get_resp.json()
                assert len(historico) >= 1, (
                    "Debería haber al menos un testimonio en el histórico."
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_historico_contiene_campos_requeridos(self):
        """
        Dado: un testimonio registrado para un vehículo.
        Cuando: se consulta el histórico.
        Entonces: cada elemento debe exponer id, reserva_id, conductor_id,
                  vehiculo_id, descripcion y created_at.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, vehiculo_id = (
                    _crear_reserva_finalizada(client, engine, "ca2-campos")
                )

                client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": "Todo perfecto.",
                    },
                    headers=_auth_headers(token_conductor),
                )

                get_resp = client.get(f"/vehiculos/{vehiculo_id}/testimonios")
                assert get_resp.status_code == 200, get_resp.text

                testimonio = get_resp.json()[0]
                campos_requeridos = {
                    "id", "reserva_id", "conductor_id",
                    "vehiculo_id", "descripcion", "created_at",
                }
                for campo in campos_requeridos:
                    assert campo in testimonio, (
                        f"El campo '{campo}' no está presente en la respuesta del histórico."
                    )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ═════════════════════════════════════════════════════════════════════════════
#  CA 3 — Inmutabilidad: rechazo de duplicados y modificaciones
# ═════════════════════════════════════════════════════════════════════════════

class TestCA3_Inmutabilidad:
    """
    CA 3: El sistema garantiza la inmutabilidad y transparencia de los
    testimonios registrados. Esto implica:
      - Rechazar un segundo POST sobre la misma reserva (409).
      - Rechazar intentos de modificación vía PUT o PATCH (405).
    """

    def test_segundo_testimonio_sobre_misma_reserva_devuelve_409(self):
        """
        Dado: un testimonio ya registrado para una reserva finalizada.
        Cuando: el conductor intenta registrar un segundo testimonio sobre
                la misma reserva.
        Entonces: el sistema rechaza con 409 Conflict.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, _ = (
                    _crear_reserva_finalizada(client, engine, "ca3-dup")
                )

                # Primer testimonio — debe ser exitoso
                primero = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": "Primera opinión.",
                    },
                    headers=_auth_headers(token_conductor),
                )
                assert primero.status_code == 201, primero.text

                # Segundo intento sobre la misma reserva — debe ser rechazado
                segundo = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": "Intento de sobrescribir.",
                    },
                    headers=_auth_headers(token_conductor),
                )
                assert segundo.status_code == 409, (
                    f"El segundo testimonio debería devolver 409, "
                    f"se recibió {segundo.status_code}: {segundo.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_testimonio_duplicado_sin_descripcion_sobre_misma_reserva_devuelve_409(self):
        """
        Caso límite: incluso si el segundo intento no tiene descripción
        (campo None), el sistema debe rechazarlo con 409 para garantizar
        la unicidad por reserva.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, _ = (
                    _crear_reserva_finalizada(client, engine, "ca3-dup-none")
                )

                primero = client.post(
                    "/testimonios",
                    json={"reserva_id": reserva_id, "descripcion": "Primer relato."},
                    headers=_auth_headers(token_conductor),
                )
                assert primero.status_code == 201, primero.text

                segundo = client.post(
                    "/testimonios",
                    json={"reserva_id": reserva_id},  # sin descripcion
                    headers=_auth_headers(token_conductor),
                )
                assert segundo.status_code == 409, (
                    f"Duplicado sin descripción debería devolver 409, "
                    f"se recibió {segundo.status_code}: {segundo.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_put_sobre_testimonio_devuelve_404_o_405(self):
        """
        Dado: un testimonio existente.
        Cuando: se intenta modificarlo con PUT /testimonios/{id}.
        Entonces: el sistema devuelve 404 o 405 (el endpoint de edición no existe).

        La inmutabilidad se garantiza por la AUSENCIA del endpoint de edición.
        FastAPI devuelve 404 para rutas inexistentes y 405 si la ruta existe
        pero el método no está registrado. Ambos códigos son prueba suficiente.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, _ = (
                    _crear_reserva_finalizada(client, engine, "ca3-put")
                )

                creacion = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": "Relato original.",
                    },
                    headers=_auth_headers(token_conductor),
                )
                assert creacion.status_code == 201, creacion.text
                testimonio_id = creacion.json()["id"]

                # Intento de modificación con PUT
                put_resp = client.put(
                    f"/testimonios/{testimonio_id}",
                    json={"descripcion": "Intento de modificar."},
                    headers=_auth_headers(token_conductor),
                )
                assert put_resp.status_code in (404, 405), (
                    f"PUT sobre testimonio debería devolver 404 o 405 (endpoint inexistente), "
                    f"se recibió {put_resp.status_code}: {put_resp.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_patch_sobre_testimonio_devuelve_404_o_405(self):
        """
        Dado: un testimonio existente.
        Cuando: se intenta modificarlo con PATCH /testimonios/{id}.
        Entonces: el sistema devuelve 404 o 405 (el endpoint de edición no existe).

        La inmutabilidad se garantiza por la AUSENCIA del endpoint de edición.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_conductor, _ = (
                    _crear_reserva_finalizada(client, engine, "ca3-patch")
                )

                creacion = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id,
                        "descripcion": "Relato original.",
                    },
                    headers=_auth_headers(token_conductor),
                )
                assert creacion.status_code == 201, creacion.text
                testimonio_id = creacion.json()["id"]

                # Intento de modificación con PATCH
                patch_resp = client.patch(
                    f"/testimonios/{testimonio_id}",
                    json={"descripcion": "Intento de parche."},
                    headers=_auth_headers(token_conductor),
                )
                assert patch_resp.status_code in (404, 405), (
                    f"PATCH sobre testimonio debería devolver 404 o 405 (endpoint inexistente), "
                    f"se recibió {patch_resp.status_code}: {patch_resp.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_testimonio_de_otra_reserva_del_mismo_vehiculo_es_aceptado(self):
        """
        Verificación de que la restricción de unicidad es por RESERVA,
        no por vehículo. Dos reservas diferentes del mismo vehículo
        pueden tener sus propios testimonios.

        Dado: un vehículo con dos reservas FINALIZADAS distintas.
        Cuando: cada conductor registra su propio testimonio.
        Entonces: ambos son aceptados con 201.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_email = "prop-ts-dos-res@autospot.com"
                vehiculo, _ = _registrar_vehiculo(client, propietario_email)
                vehiculo_id = vehiculo["id"]
                _hacer_vehiculo_reservable(engine, vehiculo_id)

                # ── Primer conductor + primera reserva ───────────────────
                _, token_c1 = _registrar_y_loguear_usuario(
                    client, "conductor-ts-r1@autospot.com"
                )
                r1 = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo_id),
                    headers=_auth_headers(token_c1),
                )
                assert r1.status_code == 201, r1.text
                reserva_id_1 = r1.json()["id"]
                _forzar_reserva_finalizada(engine, reserva_id_1)

                resp_t1 = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id_1,
                        "descripcion": "Primera experiencia.",
                    },
                    headers=_auth_headers(token_c1),
                )
                assert resp_t1.status_code == 201, (
                    f"El primer testimonio debería crearse con 201, "
                    f"se recibió {resp_t1.status_code}: {resp_t1.text}"
                )

                # ── Segundo conductor + segunda reserva del mismo vehículo ─
                _hacer_vehiculo_reservable(engine, vehiculo_id)
                _, token_c2 = _registrar_y_loguear_usuario(
                    client, "conductor-ts-r2@autospot.com"
                )
                r2 = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo_id),
                    headers=_auth_headers(token_c2),
                )
                assert r2.status_code == 201, r2.text
                reserva_id_2 = r2.json()["id"]
                _forzar_reserva_finalizada(engine, reserva_id_2)

                resp_t2 = client.post(
                    "/testimonios",
                    json={
                        "reserva_id": reserva_id_2,
                        "descripcion": "Segunda experiencia.",
                    },
                    headers=_auth_headers(token_c2),
                )
                assert resp_t2.status_code == 201, (
                    f"El segundo testimonio (distinta reserva) debería crearse con 201, "
                    f"se recibió {resp_t2.status_code}: {resp_t2.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
