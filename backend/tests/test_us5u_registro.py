"""
Tests Unitarios — US 5U: Registrarse con mail y contraseña.

Metodología: TDD (Test-Driven Development)
  - Los tests de CA 1 y CA 2 pasan en la fase ROJA (el schema ya existe).
  - Los tests de CA 4 y CA 5 fallan en la fase ROJA (el servicio es un stub).
  - Todos los tests pasarán en la fase VERDE tras implementar el servicio.

Criterios de Aceptación cubiertos:
  ┌─────┬──────────────────────────────────────────────────────────────────┐
  │ CA  │ Descripción                                                      │
  ├─────┼──────────────────────────────────────────────────────────────────┤
  │ CA1 │ Email inválido → error "Mail invalido"                           │
  │ CA2 │ Contraseña < 8 chars → "La contraseña debe tener minimo 8..."   │
  │ CA4 │ Registro exitoso: usuario creado + contraseña hasheada (hashing) │
  │ CA5 │ Email duplicado → MailExistenteError con "Mail existente"        │
  └─────┴──────────────────────────────────────────────────────────────────┘

  CA3 (botón deshabilitado sin campos) → es responsabilidad del frontend,
  no tiene cobertura de tests de backend.

Referencias:
  - docs/historias_usuario/US_5U_Registro_Mail_Contrasenia.md
  - docs/core_negocio/dominio_actores.md
"""
import pytest
from pydantic import ValidationError

from app.exceptions import MailExistenteError
from app.schemas.usuario import RegistroUsuarioSchema
from app.services.usuario import crear_usuario
from app.utils.security import verify_password


# ══════════════════════════════════════════════════════════════════════════════
#  CA 1 — Validación de formato de email
#  "Dado que un nuevo usuario intenta registrarse, cuando ingresa en el campo
#   de mail algo que no lo es, entonces el sistema tira un error de 'Mail invalido'."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1_EmailInvalido:
    """
    Verifica que el schema rechaza cualquier string que no sea un email válido
    y que el mensaje de error sea exactamente 'Mail invalido'.
    """

    def _get_errores(self, email: str) -> list[dict]:
        """Helper: levanta ValidationError y retorna la lista de errores."""
        with pytest.raises(ValidationError) as exc_info:
            RegistroUsuarioSchema(email=email, password="password123")
        return exc_info.value.errors()

    def _assert_mensaje_mail_invalido(self, errores: list[dict]) -> None:
        """Helper: verifica que al menos un error contenga el mensaje canónico."""
        mensajes = [e["msg"] for e in errores]
        assert any(
            "Mail invalido" in msg for msg in mensajes
        ), f"Se esperaba 'Mail invalido' en los errores, pero se recibió: {mensajes}"

    def test_ca1_email_sin_arroba(self):
        """'estonoesmail' no tiene @, debe fallar con 'Mail invalido'."""
        errores = self._get_errores("estonoesmail")
        self._assert_mensaje_mail_invalido(errores)

    def test_ca1_email_sin_dominio(self):
        """'usuario@' no tiene dominio, debe fallar con 'Mail invalido'."""
        errores = self._get_errores("usuario@")
        self._assert_mensaje_mail_invalido(errores)

    def test_ca1_email_sin_tld(self):
        """'usuario@dominio' no tiene TLD (.com), debe fallar."""
        errores = self._get_errores("usuario@dominio")
        self._assert_mensaje_mail_invalido(errores)

    def test_ca1_email_con_espacios(self):
        """Un email con espacios internos es inválido."""
        errores = self._get_errores("usua rio@dominio.com")
        self._assert_mensaje_mail_invalido(errores)

    def test_ca1_email_vacio(self):
        """Un string vacío no es un email válido."""
        errores = self._get_errores("")
        self._assert_mensaje_mail_invalido(errores)

    def test_ca1_email_solo_arroba(self):
        """El carácter '@' solo no es un email válido."""
        errores = self._get_errores("@")
        self._assert_mensaje_mail_invalido(errores)

    # ── Contraprueba: emails válidos NO deben lanzar error ───────────────────
    def test_ca1_email_valido_no_lanza_error(self):
        """Un email bien formado debe ser aceptado sin errores."""
        schema = RegistroUsuarioSchema(
            email="conductor@autospot.com", password="password123"
        )
        assert schema.email == "conductor@autospot.com"

    def test_ca1_email_valido_se_normaliza_a_minusculas(self):
        """El schema debe normalizar el email a minúsculas."""
        schema = RegistroUsuarioSchema(
            email="Conductor@AutoSpot.COM", password="password123"
        )
        assert schema.email == "conductor@autospot.com"


# ══════════════════════════════════════════════════════════════════════════════
#  CA 2 — Validación de longitud de contraseña
#  "Dado que un nuevo usuario intenta registrarse, cuando ingresa una contraseña
#   de menos de 8 caracteres, entonces el sistema tira un error de
#   'La contrasenia debe tener minimo 8 caracteres'."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA2_ContraseniaCorta:
    """
    Verifica que el schema rechaza contraseñas de menos de 8 caracteres
    con el mensaje de error exacto del CA 2.
    """

    MENSAJE_ESPERADO = "La contraseña debe tener minimo 8 caracteres"

    def _assert_error_contrasenia(self, password: str) -> None:
        """Helper: verifica que se lanza ValidationError con el mensaje correcto."""
        with pytest.raises(ValidationError) as exc_info:
            RegistroUsuarioSchema(email="valido@autospot.com", password=password)
        mensajes = [e["msg"] for e in exc_info.value.errors()]
        assert any(
            self.MENSAJE_ESPERADO in msg for msg in mensajes
        ), f"Se esperaba '{self.MENSAJE_ESPERADO}' pero se recibió: {mensajes}"

    def test_ca2_contrasenia_de_7_caracteres(self):
        """Exactamente 7 caracteres está un dígito por debajo del mínimo."""
        self._assert_error_contrasenia("1234567")

    def test_ca2_contrasenia_de_1_caracter(self):
        """Un único carácter es claramente inválido."""
        self._assert_error_contrasenia("a")

    def test_ca2_contrasenia_vacia(self):
        """String vacío debe fallar con el mensaje de contraseña."""
        self._assert_error_contrasenia("")

    # ── Contrapruebas: contraseñas válidas ───────────────────────────────────
    def test_ca2_contrasenia_de_exactamente_8_caracteres_es_valida(self):
        """8 caracteres es el mínimo aceptable; no debe lanzar error."""
        schema = RegistroUsuarioSchema(
            email="valido@autospot.com", password="12345678"
        )
        assert schema.password == "12345678"

    def test_ca2_contrasenia_larga_es_valida(self):
        """Una contraseña larga y segura debe ser aceptada sin error."""
        schema = RegistroUsuarioSchema(
            email="valido@autospot.com", password="MiContraseñaSegura2026!"
        )
        assert len(schema.password) > 8


# ══════════════════════════════════════════════════════════════════════════════
#  CA 4 — Registro exitoso + Hashing de contraseña
#  "Dado que un nuevo usuario intenta registrarse, cuando completa correctamente
#   ambos campos, entonces se registra exitosamente."
#
#  Requisito implícito de seguridad: la contraseña NUNCA se almacena en texto
#  plano; siempre se persiste su hash bcrypt.
#
#  ⚠️  FASE ROJA: estos tests fallan hasta implementar `crear_usuario`.
# ══════════════════════════════════════════════════════════════════════════════
class TestCA4_RegistroExitoso:
    """
    Verifica el happy path del registro y el hashing correcto de la contraseña.
    Depende del fixture `db_session` (SQLite en memoria).
    """

    def test_ca4_registro_crea_usuario_en_db(self, db_session):
        """
        El usuario creado debe tener un id asignado y el email
        normalizado en la base de datos.
        """
        schema = RegistroUsuarioSchema(
            email="nuevo@autospot.com", password="password123"
        )
        usuario = crear_usuario(db=db_session, schema=schema)

        assert usuario.id is not None, "El usuario debe tener un UUID asignado."
        assert usuario.email == "nuevo@autospot.com"
        assert usuario.is_active is True

    def test_ca4_contrasenia_no_se_almacena_en_texto_plano(self, db_session):
        """
        La columna `hashed_password` NUNCA debe contener la contraseña original.
        Esto garantiza que una filtración de DB no expone credenciales.
        """
        plain_password = "password123"
        schema = RegistroUsuarioSchema(
            email="hash@autospot.com", password=plain_password
        )
        usuario = crear_usuario(db=db_session, schema=schema)

        assert usuario.hashed_password != plain_password, (
            "La contraseña fue almacenada en texto plano. "
            "Debe aplicarse hashing bcrypt antes de persistir."
        )

    def test_ca4_hash_es_verificable_con_password_original(self, db_session):
        """
        El hash almacenado debe poder verificarse con la contraseña original
        usando `verify_password`. Esto valida la round-trip del algoritmo bcrypt.
        """
        plain_password = "MiContrasena2026"
        schema = RegistroUsuarioSchema(
            email="verify@autospot.com", password=plain_password
        )
        usuario = crear_usuario(db=db_session, schema=schema)

        assert verify_password(plain_password, usuario.hashed_password) is True, (
            "verify_password debe retornar True para la contraseña original "
            "contra el hash almacenado."
        )

    def test_ca4_password_incorrecto_no_verifica(self, db_session):
        """
        Una contraseña incorrecta no debe verificarse contra el hash.
        Valida que bcrypt distingue contraseñas distintas.
        """
        schema = RegistroUsuarioSchema(
            email="wrongpass@autospot.com", password="passwordCorrecta123"
        )
        usuario = crear_usuario(db=db_session, schema=schema)

        assert verify_password("passwordIncorrecta!", usuario.hashed_password) is False


# ══════════════════════════════════════════════════════════════════════════════
#  CA 5 — Unicidad de email (restricción de duplicados)
#  "Dado que un nuevo usuario intenta registrarse, cuando quiere registrar un
#   mail ya existente en la plataforma, entonces el sistema tira un error de
#   'Mail existente'."
#
#  ⚠️  FASE ROJA: estos tests fallan hasta implementar `crear_usuario`.
# ══════════════════════════════════════════════════════════════════════════════
class TestCA5_MailExistente:
    """
    Verifica que el servicio lanza MailExistenteError al intentar registrar
    un email que ya existe, y que el mensaje es exactamente 'Mail existente'.
    """

    def test_ca5_email_duplicado_lanza_mail_existente_error(self, db_session):
        """
        Segundo intento de registro con el mismo email debe lanzar
        MailExistenteError con el mensaje canónico del CA 5.
        """
        schema = RegistroUsuarioSchema(
            email="existente@autospot.com", password="password123"
        )
        # Primer registro — debe ser exitoso
        crear_usuario(db=db_session, schema=schema)

        # Segundo registro con el mismo email — debe fallar
        with pytest.raises(MailExistenteError) as exc_info:
            crear_usuario(db=db_session, schema=schema)

        assert str(exc_info.value) == "Mail existente", (
            f"Mensaje de error incorrecto. "
            f"Se esperaba 'Mail existente' pero se recibió: '{exc_info.value}'"
        )

    def test_ca5_email_duplicado_case_insensitive(self, db_session):
        """
        El email se normaliza a minúsculas antes de persistir.
        Un registro con 'EXISTENTE@autospot.com' después de 'existente@autospot.com'
        debe ser detectado como duplicado.
        """
        schema_original = RegistroUsuarioSchema(
            email="existente@autospot.com", password="password123"
        )
        crear_usuario(db=db_session, schema=schema_original)

        schema_uppercase = RegistroUsuarioSchema(
            email="EXISTENTE@autospot.com", password="otraContrasena456"
        )
        with pytest.raises(MailExistenteError):
            crear_usuario(db=db_session, schema=schema_uppercase)

    def test_ca5_emails_distintos_no_lanza_error(self, db_session):
        """
        Dos usuarios con emails diferentes deben poder registrarse sin conflicto.
        """
        schema_a = RegistroUsuarioSchema(
            email="usuario_a@autospot.com", password="password123"
        )
        schema_b = RegistroUsuarioSchema(
            email="usuario_b@autospot.com", password="password456"
        )
        usuario_a = crear_usuario(db=db_session, schema=schema_a)
        usuario_b = crear_usuario(db=db_session, schema=schema_b)

        assert usuario_a.id != usuario_b.id
        assert usuario_a.email != usuario_b.email
