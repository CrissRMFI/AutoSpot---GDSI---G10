"""
Tests de Integración HTTP — US 4D: Visualización de estado de solicitud de habilitación.

Endpoint principal a testear:
  GET /vehiculos/{vehiculo_id}

Contrato esperado:
  - Requiere autenticación (JWT).
  - Devuelve los detalles del vehículo, incluyendo el `estado_registro`.
  - Si el estado es "RECHAZADO", debe incluir `motivo_rechazo`.
  - Intento de habilitar/definir disponibilidad (PATCH /vehiculos/{id}/disponibilidad)
    debe fallar si el estado es "EN_REVISION" o "RECHAZADO".
"""
import uuid

from app.database import Base
from app.main import app
from tests.test_us9d_habilitar_auto_http import (
    _crear_cliente,
    _registrar_vehiculo,
    _forzar_estado_vehiculo,
    _auth_headers
)
from sqlalchemy.orm import sessionmaker
from app.models.vehiculo import Vehiculo


def _forzar_rechazo_con_motivo(engine, vehiculo_id: str, motivo: str):
    """Helper para forzar estado RECHAZADO y setear el motivo de rechazo en DB."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == uuid.UUID(vehiculo_id)).first()
        if vehiculo:
            vehiculo.estado_registro = "RECHAZADO"
            # Asumimos que el modelo Vehiculo tiene o tendrá un campo motivo_rechazo
            # Para el test, si no existe el campo en el modelo, sqlalchemy tiraría error,
            # lo cual es el comportamiento esperado en TDD (Fase Roja)
            vehiculo.motivo_rechazo = motivo
            db.commit()


class TestCA1_EtiquetasDeEstadoHTTP:
    def test_ca1_ver_estado_en_revision(self):
        """
        CA 1: Dado que envíe mi solicitud de habilitación,
        cuando consulto mi panel de control,
        entonces el sistema muestra claramente "En Revision" (estado EN_REVISION o PENDIENTE_DOCUMENTACION).
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca1_revision@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "EN_REVISION")

                response = client.get(
                    f"/vehiculos/{vehiculo['id']}",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, f"Error: {response.text}"
                body = response.json()
                assert body["estado_registro"] == "EN_REVISION"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ca1_ver_estado_aprobado(self):
        """CA 1: Estado Aprobado -> HABILITADO"""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca1_aprobado@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "HABILITADO")

                response = client.get(
                    f"/vehiculos/{vehiculo['id']}",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200
                body = response.json()
                assert body["estado_registro"] == "HABILITADO"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ca1_ver_estado_rechazado(self):
        """CA 1: Estado Rechazado -> RECHAZADO"""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca1_rechazado@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "RECHAZADO")

                response = client.get(
                    f"/vehiculos/{vehiculo['id']}",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200
                body = response.json()
                assert body["estado_registro"] == "RECHAZADO"

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestCA2_DetalleMotivoRechazoHTTP:
    def test_ca2_ver_motivo_de_rechazo(self):
        """
        CA 2: Dado que mi solicitud fue "Rechazada",
        cuando accedo al detalle,
        entonces visualizo el motivo del administrador.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca2_rechazo@autospot.com")
                motivo_esperado = "Las fotos del seguro son ilegibles."
                _forzar_rechazo_con_motivo(engine, vehiculo["id"], motivo_esperado)

                response = client.get(
                    f"/vehiculos/{vehiculo['id']}",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200
                body = response.json()
                assert body["estado_registro"] == "RECHAZADO"
                assert "motivo_rechazo" in body
                assert body["motivo_rechazo"] == motivo_esperado

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestCA3_OpcionesInactivasHTTP:
    def test_ca3_intento_habilitar_en_revision(self):
        """
        CA 3: Dado que mi estado es "En Revision",
        cuando intento acceder a "Habilitar auto" o "Definir disponibilidad",
        entonces esas opciones permanecen inactivas (rechazado por el backend).
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca3_revision@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "EN_REVISION")

                # Intentamos definir disponibilidad
                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token),
                )

                assert response.status_code in [400, 403, 409]
                assert "auto aún no fue habilitado" in response.text.lower() or "estado en_revision" in response.text.lower()

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ca3_intento_habilitar_rechazado(self):
        """
        CA 3: Dado que mi estado es "Rechazado",
        cuando intento acceder a "Habilitar auto" o "Definir disponibilidad",
        entonces el backend lo rechaza.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, token = _registrar_vehiculo(client, "ca3_rechazado@autospot.com")
                _forzar_estado_vehiculo(engine, vehiculo["id"], "RECHAZADO")

                # Intentamos definir disponibilidad
                response = client.patch(
                    f"/vehiculos/{vehiculo['id']}/disponibilidad",
                    json={"disponible": True},
                    headers=_auth_headers(token),
                )

                assert response.status_code in [400, 403, 409]
                assert "auto aún no fue habilitado" in response.text.lower() or "estado rechazado" in response.text.lower()

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

class TestSeguridadUS4DHTTP:
    def test_ver_vehiculo_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "seg1@autospot.com")

                response = client.get(f"/vehiculos/{vehiculo['id']}")
                assert response.status_code == 401

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ver_vehiculo_ajeno_devuelve_403(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo, _ = _registrar_vehiculo(client, "propietario4d@autospot.com")
                
                from tests.test_us9d_habilitar_auto_http import _registrar_y_loguear_usuario
                _, token_ajeno = _registrar_y_loguear_usuario(
                    client,
                    "espia4d@autospot.com",
                    rol="PROPIETARIO",
                )

                response = client.get(
                    f"/vehiculos/{vehiculo['id']}",
                    headers=_auth_headers(token_ajeno)
                )
                assert response.status_code == 403

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_ver_vehiculo_inexistente_devuelve_404(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                from tests.test_us9d_habilitar_auto_http import _registrar_y_loguear_usuario
                _, token = _registrar_y_loguear_usuario(
                    client,
                    "seg404@autospot.com",
                    rol="PROPIETARIO",
                )

                vehiculo_id_inexistente = str(uuid.uuid4())
                response = client.get(
                    f"/vehiculos/{vehiculo_id_inexistente}",
                    headers=_auth_headers(token)
                )
                assert response.status_code == 404

        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
