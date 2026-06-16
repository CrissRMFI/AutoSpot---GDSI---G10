"""
Tests HTTP — US 11R: Historial de conductores.

Endpoint propuesto:
  GET /admin/historial-conductores

Contrato esperado:
  - Requiere autenticación JWT con rol ADMIN (recepcionista).
  - Sin filtros devuelve la lista de conductores (rol CLIENTE) con sus
    alquileres (reservas) asociados.
  - Con query param `?usuario_id=<uuid>` devuelve únicamente los alquileres
    de ese conductor específico.
  - Si el conductor filtrado no tiene registros, devuelve lista vacía con 200.
"""
import uuid
import itertools
from decimal import Decimal
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.utils.security import hash_password
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _login_usuario,
    _registrar_vehiculo,
    _registrar_y_loguear_usuario,
)
from tests.test_us14c_obtener_codigo_reserva_http import (
    _hacer_vehiculo_reservable,
    _registrar_admin_directo,
    _payload_reserva,
)

_dni_counter = itertools.count(80_000_000)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _registrar_datos_personales(engine, usuario_id: str, nombre: str, apellido: str) -> None:
    """Inserta datos personales directamente en DB para un usuario."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    dni = str(next(_dni_counter))
    with TestingSessionLocal() as db:
        datos = DatosPersonalesUsuario(
            usuario_id=uuid.UUID(usuario_id),
            dni=dni,
            nombre=nombre,
            apellido=apellido,
            foto_dni_frente_url=f"uploads/dni/{dni}/frente.jpg",
            foto_dni_dorso_url=f"uploads/dni/{dni}/dorso.jpg",
            estado_validacion="APROBADO",
        )
        db.add(datos)
        db.commit()


def _crear_reserva_directa(
    engine,
    vehiculo_id: str,
    conductor_id: str,
    estado: str = "CONFIRMADA",
) -> None:
    """Crea una reserva directamente en DB para asociar un alquiler a un conductor."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    ahora = datetime.now(timezone.utc)
    with TestingSessionLocal() as db:
        db.add(
            Reserva(
                vehiculo_id=uuid.UUID(vehiculo_id),
                conductor_id=uuid.UUID(conductor_id),
                codigo=f"AS-{uuid.uuid4().hex[:6].upper()}",
                estado=estado,
                monto_total=Decimal("75000.00"),
                fecha_inicio=ahora - timedelta(days=5),
                fecha_fin=ahora - timedelta(days=2),
                estacion_retiro="Estación Belgrano",
            )
        )
        db.commit()


# ── CA 1: Sin filtros → lista de conductores con alquileres ─────────────────

class TestCA1_HistorialSinFiltros:
    def test_historial_sin_filtros_devuelve_conductores_con_alquileres(self):
        """
        CA 1: Dado que accedo al historial de conductores cuando hay registros,
        entonces veo la lista de conductores con sus alquileres asociados.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                # ── Setup: admin, propietario con vehículo, 2 conductores ────
                _registrar_admin_directo(engine, email="admin11r-ca1@autospot.com")
                token_admin = _login_usuario(client, "admin11r-ca1@autospot.com")

                vehiculo, _ = _registrar_vehiculo(client, "prop11r-ca1@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])

                # Conductor 1 con 1 reserva
                c1_id, _ = _registrar_y_loguear_usuario(
                    client, "conductor1-ca1@autospot.com",
                )
                _registrar_datos_personales(engine, c1_id, "Carlos", "Pérez")
                _crear_reserva_directa(engine, vehiculo["id"], c1_id)

                # Conductor 2 con 1 reserva
                c2_id, _ = _registrar_y_loguear_usuario(
                    client, "conductor2-ca1@autospot.com",
                )
                _registrar_datos_personales(engine, c2_id, "María", "García")
                _crear_reserva_directa(engine, vehiculo["id"], c2_id)

                # ── Act ──────────────────────────────────────────────────────
                response = client.get(
                    "/admin/historial-conductores",
                    headers=_auth_headers(token_admin),
                )

                # ── Assert ───────────────────────────────────────────────────
                assert response.status_code == 200, response.text
                body = response.json()
                assert isinstance(body, list)
                assert len(body) >= 2

                # Verificar estructura de cada conductor en la respuesta
                emails_en_respuesta = [c["email"] for c in body]
                assert "conductor1-ca1@autospot.com" in emails_en_respuesta
                assert "conductor2-ca1@autospot.com" in emails_en_respuesta

                # Cada conductor debe tener alquileres asociados
                for conductor in body:
                    assert "alquileres" in conductor
                    assert isinstance(conductor["alquileres"], list)

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ── CA 2: Filtro por usuario_id → solo alquileres de ese conductor ──────────

class TestCA2_HistorialFiltradoPorUsuario:
    def test_filtro_por_usuario_id_devuelve_solo_ese_conductor(self):
        """
        CA 2: Dado que veo el historial, cuando filtro por usuario,
        entonces veo únicamente los alquileres de ese conductor.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(engine, email="admin11r-ca2@autospot.com")
                token_admin = _login_usuario(client, "admin11r-ca2@autospot.com")

                vehiculo, _ = _registrar_vehiculo(client, "prop11r-ca2@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo["id"])

                # Conductor objetivo con reserva
                c1_id, _ = _registrar_y_loguear_usuario(
                    client, "conductor1-ca2@autospot.com",
                )
                _registrar_datos_personales(engine, c1_id, "Juan", "López")
                _crear_reserva_directa(engine, vehiculo["id"], c1_id)

                # Otro conductor (no debe aparecer)
                c2_id, _ = _registrar_y_loguear_usuario(
                    client, "conductor2-ca2@autospot.com",
                )
                _registrar_datos_personales(engine, c2_id, "Ana", "Martínez")
                _crear_reserva_directa(engine, vehiculo["id"], c2_id)

                # ── Act: filtrar por conductor 1 ─────────────────────────────
                response = client.get(
                    f"/admin/historial-conductores?usuario_id={c1_id}",
                    headers=_auth_headers(token_admin),
                )

                # ── Assert ───────────────────────────────────────────────────
                assert response.status_code == 200, response.text
                body = response.json()
                assert isinstance(body, list)
                assert len(body) == 1

                conductor = body[0]
                assert conductor["email"] == "conductor1-ca2@autospot.com"
                assert len(conductor["alquileres"]) >= 1

                # Verificar que el otro conductor NO aparece
                emails = [c["email"] for c in body]
                assert "conductor2-ca2@autospot.com" not in emails

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ── CA 3: Filtro sin registros → lista vacía, status 200 ────────────────────

class TestCA3_HistorialSinRegistros:
    def test_filtro_por_usuario_sin_alquileres_devuelve_lista_vacia(self):
        """
        CA 3: Dado que aplico el filtro por usuario cuando no hay registros
        para ese conductor, entonces el sistema informa que ese conductor
        no tiene historial (lista vacía, status 200).
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(engine, email="admin11r-ca3@autospot.com")
                token_admin = _login_usuario(client, "admin11r-ca3@autospot.com")

                # Conductor registrado pero SIN reservas
                c_id, _ = _registrar_y_loguear_usuario(
                    client, "conductor-ca3@autospot.com",
                )
                _registrar_datos_personales(engine, c_id, "Pedro", "Sánchez")

                # ── Act ──────────────────────────────────────────────────────
                response = client.get(
                    f"/admin/historial-conductores?usuario_id={c_id}",
                    headers=_auth_headers(token_admin),
                )

                # ── Assert ───────────────────────────────────────────────────
                assert response.status_code == 200, response.text
                body = response.json()
                assert isinstance(body, list)
                assert len(body) == 0

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_filtro_por_usuario_inexistente_devuelve_lista_vacia(self):
        """
        Variante de CA 3: UUID que no corresponde a ningún usuario registrado.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _registrar_admin_directo(engine, email="admin11r-ca3b@autospot.com")
                token_admin = _login_usuario(client, "admin11r-ca3b@autospot.com")

                usuario_id_fantasma = str(uuid.uuid4())

                response = client.get(
                    f"/admin/historial-conductores?usuario_id={usuario_id_fantasma}",
                    headers=_auth_headers(token_admin),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert isinstance(body, list)
                assert len(body) == 0

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


# ── Seguridad ────────────────────────────────────────────────────────────────

class TestSeguridad_HistorialConductoresHTTP:
    def test_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                response = client.get("/admin/historial-conductores")
                assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_usuario_no_admin_devuelve_403(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, token_cliente = _registrar_y_loguear_usuario(
                    client, "cliente-seguridad@autospot.com",
                )
                response = client.get(
                    "/admin/historial-conductores",
                    headers=_auth_headers(token_cliente),
                )
                assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
