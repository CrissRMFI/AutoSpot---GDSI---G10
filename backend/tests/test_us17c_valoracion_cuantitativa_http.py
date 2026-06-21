"""
Tests HTTP — US 17C: Valoración cuantitativa del servicio.

Metodología TDD — Fase RED:
    Estos tests deben FALLAR porque el endpoint, modelo, esquema y servicio
    de valoraciones aún no existen.

Criterios de Aceptación cubiertos:
    CA 1 & 2 — Validar rango 1–5 (enteros), rechazar valores fuera de rango
               y tipos de datos inválidos con HTTP 422.
    CA 3    — Al registrar un puntaje válido sobre una reserva FINALIZADA con
               devolución física, el sistema guarda la valoración y recalcula
               el promedio del vehículo y del propietario.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import uuid

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.reserva import Reserva
from app.models.vehiculo import Vehiculo
from app.models.usuario import Usuario
from tests.test_us14c_obtener_codigo_reserva_http import (
    _hacer_vehiculo_reservable,
    _payload_reserva,
    _registrar_admin_directo,
    _registrar_datos_personales_directo,
)
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _login_usuario,
    _registrar_vehiculo,
    _registrar_y_loguear_usuario,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _forzar_reserva_finalizada(engine, reserva_id: str) -> None:
    """
    Lleva una reserva al estado FINALIZADA con devolución física registrada,
    simulando todo el flujo completado (check-in → en curso → devuelto →
    checkout confirmado → finalizada).
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    ahora = datetime.now(timezone.utc)
    with TestingSessionLocal() as db:
        reserva = db.query(Reserva).filter(Reserva.id == uuid.UUID(reserva_id)).first()
        reserva.estado = "FINALIZADA"
        reserva.codigo_verificado_at = ahora - timedelta(days=5)
        reserva.fecha_inicio = ahora - timedelta(days=5)
        reserva.fecha_fin = ahora - timedelta(days=2)
        reserva.fecha_salida_real = ahora - timedelta(days=5)
        reserva.fecha_devolucion_real = ahora - timedelta(days=2)
        db.commit()


def _crear_reserva_finalizada(client, engine, sufijo: str):
    """
    Crea un flujo completo: propietario + vehículo + cliente + reserva,
    y fuerza la reserva a FINALIZADA con devolución.
    Devuelve (reserva_id, token_cliente, vehiculo_id, propietario_email).
    """
    propietario_email = f"prop-{sufijo}@autospot.com"
    vehiculo, _ = _registrar_vehiculo(client, propietario_email)
    _hacer_vehiculo_reservable(engine, vehiculo["id"])

    id_cliente, token_cliente = _registrar_y_loguear_usuario(
        client,
        f"cliente-{sufijo}@autospot.com",
    )
    _registrar_datos_personales_directo(engine, id_cliente)

    creacion = client.post(
        "/alquiler/reservas",
        json=_payload_reserva(vehiculo["id"]),
        headers=_auth_headers(token_cliente),
    )
    assert creacion.status_code == 201, creacion.text
    reserva_id = creacion.json()["id"]

    _forzar_reserva_finalizada(engine, reserva_id)

    return reserva_id, token_cliente, vehiculo["id"], propietario_email


def _obtener_promedio_vehiculo(engine, vehiculo_id: str) -> float | None:
    """Lee el campo calificacion_promedio del vehículo en la BD."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        vehiculo = db.query(Vehiculo).filter(
            Vehiculo.id == uuid.UUID(vehiculo_id)
        ).first()
        return getattr(vehiculo, "calificacion_promedio", None)


def _obtener_promedio_propietario(engine, propietario_email: str) -> float | None:
    """Lee el campo calificacion_promedio del propietario (usuario) en la BD."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        usuario = db.query(Usuario).filter(
            Usuario.email == propietario_email
        ).first()
        return getattr(usuario, "calificacion_promedio", None)


# ═════════════════════════════════════════════════════════════════════════════
#  CA 1 & CA 2 — Validación de rango y tipo de dato
# ═════════════════════════════════════════════════════════════════════════════

class TestCA1CA2_ValidacionRangoPuntaje:
    """
    CA 1: Solo valores de 1 a 5 (enteros).
    CA 2: Valores fuera de rango o tipos inválidos → HTTP 422.
    """

    def test_puntaje_0_devuelve_422(self):
        """Valor por debajo del mínimo (0) debe ser rechazado."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, _ = _crear_reserva_finalizada(
                    client, engine, "val-0"
                )

                response = client.post(
                    f"/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": 0},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 422, (
                    f"Puntaje 0 debería devolver 422, recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_puntaje_6_devuelve_422(self):
        """Valor por encima del máximo (6) debe ser rechazado."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, _ = _crear_reserva_finalizada(
                    client, engine, "val-6"
                )

                response = client.post(
                    f"/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": 6},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 422, (
                    f"Puntaje 6 debería devolver 422, recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_puntaje_negativo_devuelve_422(self):
        """Un valor negativo (-1) debe ser rechazado."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, _ = _crear_reserva_finalizada(
                    client, engine, "val-neg"
                )

                response = client.post(
                    f"/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": -1},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 422, (
                    f"Puntaje -1 debería devolver 422, recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_puntaje_decimal_devuelve_422(self):
        """Un valor decimal (3.5) NO es un entero válido → 422."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, _ = _crear_reserva_finalizada(
                    client, engine, "val-dec"
                )

                response = client.post(
                    f"/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": 3.5},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 422, (
                    f"Puntaje 3.5 debería devolver 422, recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_puntaje_texto_devuelve_422(self):
        """Un valor de texto ('abc') debe ser rechazado."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, _ = _crear_reserva_finalizada(
                    client, engine, "val-txt"
                )

                response = client.post(
                    f"/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": "abc"},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 422, (
                    f"Puntaje 'abc' debería devolver 422, recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_puntaje_null_devuelve_422(self):
        """Enviar puntaje null debe ser rechazado."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, _ = _crear_reserva_finalizada(
                    client, engine, "val-null"
                )

                response = client.post(
                    f"/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": None},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 422, (
                    f"Puntaje null debería devolver 422, recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ═════════════════════════════════════════════════════════════════════════════
#  CA 1 — Valores válidos en los límites (1 y 5)
# ═════════════════════════════════════════════════════════════════════════════

class TestCA1_LimitesValidos:
    """Los bordes del rango (1 y 5) deben ser aceptados."""

    def test_puntaje_1_es_aceptado(self):
        """El límite inferior (1) es válido → 201."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, _ = _crear_reserva_finalizada(
                    client, engine, "val-1"
                )

                response = client.post(
                    f"/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": 1},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 201, (
                    f"Puntaje 1 debería devolver 201, recibió {response.status_code}: {response.text}"
                )
                body = response.json()
                assert body["puntaje"] == 1
                assert body["reserva_id"] == reserva_id
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_puntaje_5_es_aceptado(self):
        """El límite superior (5) es válido → 201."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, _ = _crear_reserva_finalizada(
                    client, engine, "val-5"
                )

                response = client.post(
                    f"/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": 5},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 201, (
                    f"Puntaje 5 debería devolver 201, recibió {response.status_code}: {response.text}"
                )
                body = response.json()
                assert body["puntaje"] == 5
                assert body["reserva_id"] == reserva_id
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ═════════════════════════════════════════════════════════════════════════════
#  CA 3 — Consolidación: promedio de vehículo y propietario
# ═════════════════════════════════════════════════════════════════════════════

class TestCA3_ConsolidacionPromedios:
    """
    Al registrar un puntaje válido en una reserva FINALIZADA con devolución
    física, el sistema debe:
      1. Guardar la valoración en la BD.
      2. Recalcular y actualizar el promedio del vehículo.
      3. Recalcular y actualizar el promedio del propietario (dueño).
    """

    def test_valoracion_actualiza_promedio_vehiculo_y_propietario(self):
        """
        Dado: una reserva finalizada con devolución.
        Cuando: el conductor envía puntaje 4.
        Entonces: el promedio del vehículo y del propietario se actualizan a 4.0.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, vehiculo_id, prop_email = (
                    _crear_reserva_finalizada(client, engine, "prom-1")
                )

                response = client.post(
                    f"/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": 4},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 201, response.text

                # Verificar promedio del vehículo en la BD
                promedio_vehiculo = _obtener_promedio_vehiculo(engine, vehiculo_id)
                assert promedio_vehiculo is not None, (
                    "El vehículo debería tener un campo calificacion_promedio"
                )
                assert float(promedio_vehiculo) == 4.0, (
                    f"Promedio del vehículo esperado 4.0, obtenido {promedio_vehiculo}"
                )

                # Verificar promedio del propietario en la BD
                promedio_propietario = _obtener_promedio_propietario(engine, prop_email)
                assert promedio_propietario is not None, (
                    "El propietario debería tener un campo calificacion_promedio"
                )
                assert float(promedio_propietario) == 4.0, (
                    f"Promedio del propietario esperado 4.0, obtenido {promedio_propietario}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_dos_valoraciones_recalculan_promedio(self):
        """
        Dado: dos reservas finalizadas del mismo vehículo/propietario.
        Cuando: el conductor valora la primera con 4 y la segunda con 2.
        Entonces: el promedio de vehículo y propietario se actualiza a 3.0.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                # ── Primera reserva con puntaje 4 ────────────────────────
                prop_email = "prop-prom2@autospot.com"
                vehiculo, _ = _registrar_vehiculo(client, prop_email)
                vehiculo_id = vehiculo["id"]
                _hacer_vehiculo_reservable(engine, vehiculo_id)

                id_c1, token_c1 = _registrar_y_loguear_usuario(
                    client, "cliente-prom2a@autospot.com"
                )
                _registrar_datos_personales_directo(engine, id_c1)

                r1 = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo_id),
                    headers=_auth_headers(token_c1),
                )
                assert r1.status_code == 201, r1.text
                reserva_id_1 = r1.json()["id"]
                _forzar_reserva_finalizada(engine, reserva_id_1)

                resp1 = client.post(
                    "/valoraciones",
                    json={"reserva_id": reserva_id_1, "puntaje": 4},
                    headers=_auth_headers(token_c1),
                )
                assert resp1.status_code == 201, resp1.text

                # ── Segunda reserva con puntaje 2 ────────────────────────
                # Necesitamos habilitar el vehículo de nuevo para la segunda reserva
                _hacer_vehiculo_reservable(engine, vehiculo_id)

                id_c2, token_c2 = _registrar_y_loguear_usuario(
                    client, "cliente-prom2b@autospot.com"
                )
                _registrar_datos_personales_directo(engine, id_c2)
                r2 = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo_id),
                    headers=_auth_headers(token_c2),
                )
                assert r2.status_code == 201, r2.text
                reserva_id_2 = r2.json()["id"]
                _forzar_reserva_finalizada(engine, reserva_id_2)

                resp2 = client.post(
                    "/valoraciones",
                    json={"reserva_id": reserva_id_2, "puntaje": 2},
                    headers=_auth_headers(token_c2),
                )
                assert resp2.status_code == 201, resp2.text

                # ── Verificar promedios ──────────────────────────────────
                promedio_vehiculo = _obtener_promedio_vehiculo(engine, vehiculo_id)
                assert float(promedio_vehiculo) == 3.0, (
                    f"Promedio del vehículo esperado 3.0 tras (4+2)/2, obtenido {promedio_vehiculo}"
                )

                promedio_propietario = _obtener_promedio_propietario(engine, prop_email)
                assert float(promedio_propietario) == 3.0, (
                    f"Promedio del propietario esperado 3.0 tras (4+2)/2, obtenido {promedio_propietario}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_reserva_no_finalizada_no_permite_valorar(self):
        """
        Solo se puede valorar una reserva FINALIZADA con devolución registrada.
        Una reserva EN_CURSO debe devolver 400.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "prop-nofin@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])

                id_cliente, token_cliente = _registrar_y_loguear_usuario(
                    client, "cliente-nofin@autospot.com"
                )
                _registrar_datos_personales_directo(engine, id_cliente)

                creacion = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo["id"]),
                    headers=_auth_headers(token_cliente),
                )
                assert creacion.status_code == 201, creacion.text
                reserva_id = creacion.json()["id"]

                # Forzar estado EN_CURSO (sin devolución)
                TestingSessionLocal = sessionmaker(
                    autocommit=False, autoflush=False, bind=engine
                )
                ahora = datetime.now(timezone.utc)
                with TestingSessionLocal() as db:
                    reserva = db.query(Reserva).filter(
                        Reserva.id == uuid.UUID(reserva_id)
                    ).first()
                    reserva.estado = "EN_CURSO"
                    reserva.fecha_salida_real = ahora - timedelta(days=1)
                    db.commit()

                response = client.post(
                    "/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": 3},
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 400, (
                    f"Reserva EN_CURSO no debería aceptar valoración, "
                    f"recibió {response.status_code}: {response.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_valoracion_duplicada_devuelve_409(self):
        """No se puede valorar la misma reserva dos veces."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                reserva_id, token_cliente, _, _ = _crear_reserva_finalizada(
                    client, engine, "val-dup"
                )

                primera = client.post(
                    "/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": 4},
                    headers=_auth_headers(token_cliente),
                )
                assert primera.status_code == 201, primera.text

                segunda = client.post(
                    "/valoraciones",
                    json={"reserva_id": reserva_id, "puntaje": 3},
                    headers=_auth_headers(token_cliente),
                )
                assert segunda.status_code == 409, (
                    f"Valoración duplicada debería devolver 409, "
                    f"recibió {segunda.status_code}: {segunda.text}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_promedio_propietario_es_promedio_de_sus_vehiculos(self):
        """
        Regla de negocio: el promedio del propietario se calcula como el
        promedio de los promedios de TODOS sus vehículos.

        Dado: un propietario con 2 autos.
              Auto A recibe puntaje 2, Auto B recibe puntaje 4.
        Entonces: promedio Auto A = 2.0, promedio Auto B = 4.0,
                  promedio propietario = (2.0 + 4.0) / 2 = 3.0.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                # ── Registrar propietario con 2 vehículos ────────────────
                prop_email = "prop-2autos@autospot.com"
                vehiculo_a, token_prop = _registrar_vehiculo(client, prop_email)
                vehiculo_a_id = vehiculo_a["id"]
                _hacer_vehiculo_reservable(engine, vehiculo_a_id)

                # Segundo vehículo del mismo propietario
                response_b = client.post(
                    f"/usuarios/{vehiculo_a['propietario_id']}/vehiculos",
                    json={
                        "marca": "Ford",
                        "modelo": "Focus",
                        "anio": 2021,
                        "tipo_transmision": "MANUAL",
                        "capacidad": 5,
                        "categoria": "SEDAN",
                        "tipo_combustible": "NAFTA",
                        "pets_friendly": False,
                        "kilometros": 50000,
                        "fotos": [
                            {"lado": "FRENTE", "url": "url1", "formato": "jpg", "tamanio_bytes": 100},
                            {"lado": "TRASERA", "url": "url2", "formato": "jpg", "tamanio_bytes": 100},
                            {"lado": "LATERAL_IZQUIERDO", "url": "url3", "formato": "jpg", "tamanio_bytes": 100},
                            {"lado": "LATERAL_DERECHO", "url": "url4", "formato": "jpg", "tamanio_bytes": 100},
                            {"lado": "INTERIOR", "url": "url5", "formato": "jpg", "tamanio_bytes": 100},
                        ],
                    },
                    headers=_auth_headers(token_prop),
                )
                assert response_b.status_code == 201, response_b.text
                vehiculo_b_id = response_b.json()["id"]
                _hacer_vehiculo_reservable(engine, vehiculo_b_id)

                # ── Cliente 1 reserva Auto A y lo califica con 2 ─────────
                id_ci, token_c1 = _registrar_y_loguear_usuario(
                    client, "c1-2autos@autospot.com"
                )
                _registrar_datos_personales_directo(engine, id_ci)
                r1 = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo_a_id),
                    headers=_auth_headers(token_c1),
                )
                assert r1.status_code == 201, r1.text
                reserva_a_id = r1.json()["id"]
                _forzar_reserva_finalizada(engine, reserva_a_id)

                val_a = client.post(
                    "/valoraciones",
                    json={"reserva_id": reserva_a_id, "puntaje": 2},
                    headers=_auth_headers(token_c1),
                )
                assert val_a.status_code == 201, val_a.text

                # ── Cliente 2 reserva Auto B y lo califica con 4 ─────────
                _hacer_vehiculo_reservable(engine, vehiculo_b_id)
                id_c2, token_c2 = _registrar_y_loguear_usuario(
                    client, "c2-2autos@autospot.com"
                )
                _registrar_datos_personales_directo(engine, id_c2)
                r2 = client.post(
                    "/alquiler/reservas",
                    json=_payload_reserva(vehiculo_b_id),
                    headers=_auth_headers(token_c2),
                )
                assert r2.status_code == 201, r2.text
                reserva_b_id = r2.json()["id"]
                _forzar_reserva_finalizada(engine, reserva_b_id)

                val_b = client.post(
                    "/valoraciones",
                    json={"reserva_id": reserva_b_id, "puntaje": 4},
                    headers=_auth_headers(token_c2),
                )
                assert val_b.status_code == 201, val_b.text

                # ── Verificar promedios ──────────────────────────────────
                prom_a = _obtener_promedio_vehiculo(engine, vehiculo_a_id)
                assert float(prom_a) == 2.0, (
                    f"Promedio Auto A esperado 2.0, obtenido {prom_a}"
                )

                prom_b = _obtener_promedio_vehiculo(engine, vehiculo_b_id)
                assert float(prom_b) == 4.0, (
                    f"Promedio Auto B esperado 4.0, obtenido {prom_b}"
                )

                # Promedio del propietario = (2.0 + 4.0) / 2 = 3.0
                prom_prop = _obtener_promedio_propietario(engine, prop_email)
                assert prom_prop is not None, (
                    "El propietario debería tener calificacion_promedio"
                )
                assert float(prom_prop) == 3.0, (
                    f"Promedio propietario esperado 3.0 (avg de autos 2.0 y 4.0), "
                    f"obtenido {prom_prop}"
                )
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
