"""
Tests de Integración HTTP — US 5U: POST /usuarios/registro.

Metodología: TDD (fase VERDE desde el inicio, porque el test se escribe
con el controlador ya implementado).

Estrategia de tests:
    - Se usa `httpx.TestClient` de FastAPI, que permite levantar la app
      en memoria sin necesidad de un servidor real.
    - El fixture `client` (definido en conftest.py) inyecta una DB PostgreSQL
      de test limpia por cada test usando `app.dependency_overrides`.
    - Cada test recibe un cliente limpio con DB vacía → idempotencia total.

Criterios de Aceptación cubiertos en esta suite:
    ┌─────┬──────────────────────────────────────────────────────────────────┐
    │ CA  │ Descripción                                                      │
    ├─────┼──────────────────────────────────────────────────────────────────┤
    │ CA1 │ Email inválido           → HTTP 422                              │
    │ CA2 │ Contraseña < 8 chars     → HTTP 422                              │
    │ CA4 │ Registro exitoso         → HTTP 201 + body UsuarioPublicoSchema  │
    │ CA5 │ Email duplicado          → HTTP 409 + detail "Mail existente"    │
    └─────┴──────────────────────────────────────────────────────────────────┘

    CA3 (botón deshabilitado) → responsabilidad del frontend; sin cobertura backend.

Referencias:
    - docs/historias_usuario/US_5U_Registro_Mail_Contrasenia.md
    - docs/core_negocio/dominio_actores.md
"""
import pytest
from fastapi.testclient import TestClient


# ── Helpers ───────────────────────────────────────────────────────────────────
_ENDPOINT = "/usuarios/registro"

_PAYLOAD_VALIDO = {
    "email": "conductor@autospot.com",
    "password": "password123",
}


# ══════════════════════════════════════════════════════════════════════════════
#  CA 4 — Registro exitoso
#  "Dado que un nuevo usuario intenta registrarse, cuando completa correctamente
#   ambos campos, entonces se registra exitosamente."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA4_RegistroExitosoHTTP:
    """
    Verifica el happy path a nivel HTTP:
      - Status code 201 Created.
      - Body con el schema público (id, email, is_active).
      - Ausencia de datos sensibles (hashed_password) en la respuesta.
    """

    def test_ca4_devuelve_201_created(self, client: TestClient):
        """El registro exitoso debe responder con HTTP 201."""
        response = client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)
        assert response.status_code == 201, (
            f"Se esperaba 201, se recibió {response.status_code}. "
            f"Body: {response.text}"
        )

    def test_ca4_body_contiene_id_email_is_active(self, client: TestClient):
        """La respuesta debe incluir `id`, `email` e `is_active`."""
        response = client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)
        body = response.json()

        assert "id" in body, f"Falta campo 'id' en el body: {body}"
        assert "email" in body, f"Falta campo 'email' en el body: {body}"
        assert "is_active" in body, f"Falta campo 'is_active' en el body: {body}"

    def test_ca4_email_en_respuesta_es_normalizado_a_minusculas(self, client: TestClient):
        """El email devuelto debe estar en minúsculas (normalización del schema)."""
        payload = {"email": "Conductor@AutoSpot.COM", "password": "password123"}
        response = client.post(_ENDPOINT, json=payload)
        body = response.json()

        assert body["email"] == "conductor@autospot.com", (
            f"El email no fue normalizado: {body['email']}"
        )

    def test_ca4_is_active_es_true_por_defecto(self, client: TestClient):
        """Un usuario recién registrado debe tener `is_active = True`."""
        response = client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)
        body = response.json()

        assert body["is_active"] is True

    def test_ca4_id_es_uuid_valido(self, client: TestClient):
        """El campo `id` debe ser un UUID válido en formato string."""
        import uuid
        response = client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)
        body = response.json()

        try:
            uuid.UUID(body["id"])
        except (ValueError, KeyError) as exc:
            pytest.fail(f"El campo 'id' no es un UUID válido: {body.get('id')} — {exc}")

    def test_ca4_respuesta_no_expone_hashed_password(self, client: TestClient):
        """
        La respuesta NUNCA debe exponer `hashed_password` ni `password`.
        Una filtración aquí sería una vulnerabilidad de seguridad crítica.
        """
        response = client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)
        body = response.json()

        assert "hashed_password" not in body, (
            "¡VULNERABILIDAD! `hashed_password` está expuesto en la respuesta."
        )
        assert "password" not in body, (
            "¡VULNERABILIDAD! `password` está expuesto en la respuesta."
        )

    def test_ca4_content_type_es_json(self, client: TestClient):
        """La respuesta debe tener Content-Type application/json."""
        response = client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)
        assert "application/json" in response.headers.get("content-type", "")


# ══════════════════════════════════════════════════════════════════════════════
#  CA 5 — Email duplicado → 409 Conflict
#  "Dado que un nuevo usuario intenta registrarse, cuando quiere registrar un
#   mail ya existente en la plataforma, entonces el sistema tira un error de
#   'Mail existente'."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA5_MailExistenteHTTP:
    """
    Verifica que el sistema retorna 409 Conflict cuando el email ya está
    registrado, con el mensaje canónico "Mail existente".
    """

    def test_ca5_segundo_registro_devuelve_409(self, client: TestClient):
        """El segundo intento de registro con el mismo email debe retornar 409."""
        # Primer registro — debe ser exitoso
        client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)

        # Segundo registro — debe fallar con 409
        response = client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)
        assert response.status_code == 409, (
            f"Se esperaba 409, se recibió {response.status_code}. "
            f"Body: {response.text}"
        )

    def test_ca5_detail_contiene_mensaje_canonico(self, client: TestClient):
        """El body del 409 debe contener `detail: 'Mail existente'`."""
        client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)
        response = client.post(_ENDPOINT, json=_PAYLOAD_VALIDO)

        body = response.json()
        assert body.get("detail") == "Mail existente", (
            f"Mensaje de error incorrecto. "
            f"Se esperaba 'Mail existente' pero se recibió: {body.get('detail')}"
        )

    def test_ca5_email_duplicado_case_insensitive(self, client: TestClient):
        """
        Registrar primero en minúsculas y luego en mayúsculas debe
        ser detectado como duplicado (normalización en el schema).
        """
        payload_lower = {"email": "existente@autospot.com", "password": "password123"}
        payload_upper = {"email": "EXISTENTE@autospot.com", "password": "otraPassword456"}

        client.post(_ENDPOINT, json=payload_lower)
        response = client.post(_ENDPOINT, json=payload_upper)

        assert response.status_code == 409

    def test_ca5_emails_distintos_permiten_dos_registros(self, client: TestClient):
        """Dos usuarios con emails diferentes deben poder registrarse (ambos 201)."""
        payload_a = {"email": "usuario_a@autospot.com", "password": "password123"}
        payload_b = {"email": "usuario_b@autospot.com", "password": "password456"}

        response_a = client.post(_ENDPOINT, json=payload_a)
        response_b = client.post(_ENDPOINT, json=payload_b)

        assert response_a.status_code == 201
        assert response_b.status_code == 201
        assert response_a.json()["id"] != response_b.json()["id"]


# ══════════════════════════════════════════════════════════════════════════════
#  CA 1 — Email inválido → 422 Unprocessable Entity
#  "Dado que un nuevo usuario intenta registrarse, cuando ingresa en el campo
#   de mail algo que no lo es, entonces el sistema tira un error de 'Mail invalido'."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1_EmailInvalidoHTTP:
    """
    Verifica que FastAPI retorna 422 cuando el email tiene formato incorrecto
    y que el mensaje de validación es el canónico del CA 1.
    """

    def _post_email_invalido(self, client: TestClient, email: str):
        return client.post(
            _ENDPOINT,
            json={"email": email, "password": "password123"},
        )

    def _assert_422_con_mensaje(self, response, mensaje_esperado: str = "Mail invalido"):
        assert response.status_code == 422, (
            f"Se esperaba 422, se recibió {response.status_code}. "
            f"Body: {response.text}"
        )
        errores = response.json().get("detail", [])
        mensajes = [e.get("msg", "") for e in errores]
        assert any(mensaje_esperado in msg for msg in mensajes), (
            f"Se esperaba '{mensaje_esperado}' en los errores, "
            f"pero se recibió: {mensajes}"
        )

    def test_ca1_email_sin_arroba_devuelve_422(self, client: TestClient):
        """'estonoesmail' → 422 con mensaje 'Mail invalido'."""
        response = self._post_email_invalido(client, "estonoesmail")
        self._assert_422_con_mensaje(response)

    def test_ca1_email_sin_dominio_devuelve_422(self, client: TestClient):
        """'usuario@' → 422 con mensaje 'Mail invalido'."""
        response = self._post_email_invalido(client, "usuario@")
        self._assert_422_con_mensaje(response)

    def test_ca1_email_vacio_devuelve_422(self, client: TestClient):
        """String vacío → 422 con mensaje 'Mail invalido'."""
        response = self._post_email_invalido(client, "")
        self._assert_422_con_mensaje(response)

    def test_ca1_email_sin_tld_devuelve_422(self, client: TestClient):
        """'usuario@dominio' sin TLD → 422."""
        response = self._post_email_invalido(client, "usuario@dominio")
        self._assert_422_con_mensaje(response)


# ══════════════════════════════════════════════════════════════════════════════
#  CA 2 — Contraseña corta → 422 Unprocessable Entity
#  "Dado que un nuevo usuario intenta registrarse, cuando ingresa una contraseña
#   de menos de 8 caracteres, entonces el sistema tira un error de
#   'La contraseña debe tener minimo 8 caracteres'."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA2_ContraseniaHTTP:
    """
    Verifica que FastAPI retorna 422 cuando la contraseña tiene menos de 8
    caracteres, con el mensaje de error canónico del CA 2.
    """

    _MENSAJE_CA2 = "La contraseña debe tener minimo 8 caracteres"

    def _post_password_corta(self, client: TestClient, password: str):
        return client.post(
            _ENDPOINT,
            json={"email": "valido@autospot.com", "password": password},
        )

    def test_ca2_password_de_7_chars_devuelve_422(self, client: TestClient):
        """7 caracteres → 422 con mensaje de contraseña."""
        response = self._post_password_corta(client, "1234567")
        assert response.status_code == 422
        errores = response.json().get("detail", [])
        mensajes = [e.get("msg", "") for e in errores]
        assert any(self._MENSAJE_CA2 in msg for msg in mensajes), (
            f"Mensaje esperado no encontrado. Recibido: {mensajes}"
        )

    def test_ca2_password_vacia_devuelve_422(self, client: TestClient):
        """Contraseña vacía → 422."""
        response = self._post_password_corta(client, "")
        assert response.status_code == 422

    def test_ca2_password_de_8_chars_devuelve_201(self, client: TestClient):
        """8 caracteres es el mínimo válido → debe retornar 201."""
        response = self._post_password_corta(client, "12345678")
        assert response.status_code == 201


# ══════════════════════════════════════════════════════════════════════════════
#  Validaciones de payload malformado
# ══════════════════════════════════════════════════════════════════════════════
class TestPayloadMalformado:
    """
    Verifica comportamiento ante payloads incompletos o sin campos requeridos.
    FastAPI/Pydantic gestiona estos casos automáticamente con 422.
    """

    def test_payload_sin_email_devuelve_422(self, client: TestClient):
        """Body sin campo `email` → 422."""
        response = client.post(_ENDPOINT, json={"password": "password123"})
        assert response.status_code == 422

    def test_payload_sin_password_devuelve_422(self, client: TestClient):
        """Body sin campo `password` → 422."""
        response = client.post(_ENDPOINT, json={"email": "valido@autospot.com"})
        assert response.status_code == 422

    def test_payload_vacio_devuelve_422(self, client: TestClient):
        """Body vacío → 422."""
        response = client.post(_ENDPOINT, json={})
        assert response.status_code == 422

    def test_metodo_get_no_permitido(self, client: TestClient):
        """GET /usuarios/registro no está definido → 405 Method Not Allowed."""
        response = client.get("/usuarios/registro")
        assert response.status_code == 405
