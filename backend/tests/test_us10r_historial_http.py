"""
Pruebas HTTP (Integración) — US 10R: Historial de autos.
"""
from fastapi.testclient import TestClient

from app.database import Base
from app.main import app
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _login_usuario,
)
from tests.test_us14c_obtener_codigo_reserva_http import (
    _registrar_admin_directo,
)

def test_historial_autos_sin_permisos():
    """Valida que se requiera autenticación y rol de ADMIN."""
    engine, client_context = _crear_cliente()
    try:
        with client_context as client:
            response = client.get("/admin/historial-autos")
            assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_historial_autos_admin():
    """Valida el acceso correcto para un administrador."""
    engine, client_context = _crear_cliente()
    try:
        with client_context as client:
            _registrar_admin_directo(engine, email="admin-autos@autospot.com")
            token_admin = _login_usuario(client, "admin-autos@autospot.com")

            response = client.get(
                "/admin/historial-autos",
                headers=_auth_headers(token_admin)
            )
            assert response.status_code == 200
            assert isinstance(response.json(), list)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_historial_autos_con_filtros():
    """Valida que el endpoint acepte los query params de filtrado sin error."""
    engine, client_context = _crear_cliente()
    try:
        with client_context as client:
            _registrar_admin_directo(engine, email="admin-autos-filtros@autospot.com")
            token_admin = _login_usuario(client, "admin-autos-filtros@autospot.com")

            response = client.get(
                "/admin/historial-autos?estacion=Obelisco&patente=AB123&fecha=2026-06-16",
                headers=_auth_headers(token_admin)
            )
            assert response.status_code == 200
            assert isinstance(response.json(), list)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()
