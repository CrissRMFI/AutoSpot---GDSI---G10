"""
Tests de Integración HTTP — US 3U: POST /usuarios/logout.

Metodología: TDD (fase VERDE).

Estrategia:
  - Se usa el fixture `client` centralizado (conftest.py) que inyecta una DB
    PostgreSQL de test limpia por cada test usando `app.dependency_overrides`.

Criterios de Aceptación cubiertos:
    CA1: Logout manual — el usuario solicita cerrar sesión y el sistema
         invalida sus permisos de acceso de forma inmediata.
    CA2: Expiración por inactividad — un token cuyo tiempo de vida superó
         el límite de seguridad es rechazado automáticamente.
"""
from datetime import timedelta

from fastapi.testclient import TestClient
from app.utils.security import crear_access_token


# ── Constantes y helpers ──────────────────────────────────────────────────────

_ENDPOINT_REGISTRO = "/usuarios/registro"
_ENDPOINT_LOGIN = "/usuarios/login"
_ENDPOINT_LOGOUT = "/usuarios/logout"

_TEST_EMAIL = "logout@autospot.com"
_TEST_PASSWORD = "Password123!"


def _registrar_usuario(client: TestClient, email: str = _TEST_EMAIL, password: str = _TEST_PASSWORD):
    """Registra un usuario de prueba."""
    return client.post(_ENDPOINT_REGISTRO, json={"email": email, "password": password})


def _obtener_token(client: TestClient, email: str = _TEST_EMAIL, password: str = _TEST_PASSWORD) -> str:
    """Registra un usuario, hace login y devuelve el access_token."""
    _registrar_usuario(client, email, password)
    response = client.post(_ENDPOINT_LOGIN, json={"email": email, "password": password})
    return response.json()["access_token"]


def _auth_header(token: str) -> dict:
    """Construye el header Authorization: Bearer <token>."""
    return {"Authorization": f"Bearer {token}"}


# ── CA1: Logout manual ───────────────────────────────────────────────────────

class TestCA1_LogoutManualHTTP:
    """
    CA1: Dado que un usuario está activo en plataforma,
         cuando solicita la finalización de su sesión,
         entonces el sistema debe invalidar los permisos de acceso actuales
         de forma inmediata, requiriendo nueva autenticación.
    """

    def test_logout_exitoso_devuelve_200(self, client: TestClient):
        """Logout con token válido → 200 y mensaje de confirmación."""
        token = _obtener_token(client)

        response = client.post(_ENDPOINT_LOGOUT, headers=_auth_header(token))

        assert response.status_code == 200
        assert response.json()["detail"] == "Sesión finalizada correctamente"

    def test_logout_sin_token_devuelve_401(self, client: TestClient):
        """Logout sin header Authorization → 401 Unauthorized."""
        response = client.post(_ENDPOINT_LOGOUT)

        assert response.status_code == 401

    def test_logout_con_token_invalido_devuelve_401(self, client: TestClient):
        """Logout con token malformado/falsificado → 401 Unauthorized."""
        response = client.post(
            _ENDPOINT_LOGOUT,
            headers=_auth_header("token.invalido.falsificado"),
        )

        assert response.status_code == 401

    def test_token_invalidado_tras_logout_no_permite_segundo_uso(self, client: TestClient):
        """
        Después del logout, el mismo token ya no es válido.
        Un segundo POST /logout con el mismo token → 401.
        Esto prueba la invalidación inmediata (blacklist del CA1).
        """
        token = _obtener_token(client)

        # Primer logout — exitoso
        resp_1 = client.post(_ENDPOINT_LOGOUT, headers=_auth_header(token))
        assert resp_1.status_code == 200

        # Segundo intento con el mismo token — rechazado
        resp_2 = client.post(_ENDPOINT_LOGOUT, headers=_auth_header(token))
        assert resp_2.status_code == 401


# ── CA2: Expiración por inactividad ──────────────────────────────────────────

class TestCA2_ExpiracionInactividadHTTP:
    """
    CA2: Dado que existe una sesión sin actividad detectada,
         cuando el tiempo transcurrido supera el límite de seguridad,
         entonces el sistema debe finalizar la sesión automáticamente.
    """

    def test_login_devuelve_access_token(self, client: TestClient):
        """
        Pre-condición: el login debe emitir un access_token JWT
        para que el mecanismo de expiración funcione.
        """
        _registrar_usuario(client)
        response = client.post(
            _ENDPOINT_LOGIN,
            json={"email": _TEST_EMAIL, "password": _TEST_PASSWORD},
        )

        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_token_expirado_devuelve_401(self, client: TestClient):
        """
        Un token cuyo `exp` ya pasó debe ser rechazado con 401,
        simulando la expiración automática por inactividad.
        """
        token_expirado = crear_access_token(
            data={"sub": "00000000-0000-0000-0000-000000000000"},
            expires_delta=timedelta(seconds=-1),
        )

        response = client.post(
            _ENDPOINT_LOGOUT,
            headers=_auth_header(token_expirado),
        )

        assert response.status_code == 401
