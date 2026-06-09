"""
Tests HTTP — Suscripciones Web Push.
"""
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.push_subscription import PushSubscription


_ENDPOINT_REGISTRO = "/usuarios/registro"
_ENDPOINT_LOGIN = "/usuarios/login"
_ENDPOINT_LOGOUT = "/usuarios/logout"
_ENDPOINT_PUSH = "/notificaciones/push/suscripciones"
_PASSWORD = "Password123!"


def _registrar_y_loguear(client: TestClient, email: str) -> str:
    client.post(
        _ENDPOINT_REGISTRO,
        json={"email": email, "password": _PASSWORD},
    )
    response = client.post(
        _ENDPOINT_LOGIN,
        json={"email": email, "password": _PASSWORD},
    )
    return response.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _payload(endpoint: str, p256dh: str = "p256dh-test") -> dict:
    return {
        "endpoint": endpoint,
        "expirationTime": None,
        "keys": {
            "p256dh": p256dh,
            "auth": "auth-test",
        },
    }


def _contar_suscripciones(endpoint: str) -> int:
    override = app.dependency_overrides[get_db]
    db_gen = override()
    db = next(db_gen)
    try:
        return (
            db.query(PushSubscription)
            .filter(PushSubscription.endpoint == endpoint)
            .count()
        )
    finally:
        db_gen.close()


def test_registra_y_actualiza_suscripcion_push(client: TestClient):
    token = _registrar_y_loguear(client, "push-registro@autospot.com")
    endpoint = "https://push.example.test/subscription/registro"

    response = client.post(
        _ENDPOINT_PUSH,
        headers={**_auth_header(token), "User-Agent": "pytest-browser"},
        json=_payload(endpoint),
    )

    assert response.status_code == 201
    assert response.json()["endpoint"] == endpoint
    assert _contar_suscripciones(endpoint) == 1

    response_actualizacion = client.post(
        _ENDPOINT_PUSH,
        headers=_auth_header(token),
        json=_payload(endpoint, p256dh="p256dh-actualizado"),
    )

    assert response_actualizacion.status_code == 201
    assert _contar_suscripciones(endpoint) == 1


def test_logout_elimina_suscripcion_push_especifica(client: TestClient):
    token = _registrar_y_loguear(client, "push-logout@autospot.com")
    endpoint = "https://push.example.test/subscription/logout"

    response_registro = client.post(
        _ENDPOINT_PUSH,
        headers=_auth_header(token),
        json=_payload(endpoint),
    )
    assert response_registro.status_code == 201
    assert _contar_suscripciones(endpoint) == 1

    response_logout = client.post(
        _ENDPOINT_LOGOUT,
        headers=_auth_header(token),
        json={"endpoint": endpoint},
    )

    assert response_logout.status_code == 200
    assert _contar_suscripciones(endpoint) == 0
