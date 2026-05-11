"""
Tests Unitarios — US 1U: Registro datos personales.

Historia de Usuario:
  Como nuevo usuario registrado en la plataforma,
  quiero registrarme mi documentación personal,
  para constatar mi identidad.

Criterios de Aceptación cubiertos inicialmente:
  ┌─────┬──────────────────────────────────────────────────────────────────┐
  │ CA  │ Descripción                                                      │
  ├─────┼──────────────────────────────────────────────────────────────────┤
  │ CA1 │ Cuenta creada + carga DNI, nombre y apellido                     │
  │ CA2 │ Cuenta creada + sube foto frente y dorso del DNI                 │
│ CA3 │ Campo obligatorio omitido o inválido → no registra e informa error│
  └─────┴──────────────────────────────────────────────────────────────────┘

Referencias:
  - Backlog Sprint 1 — US 1U Registro datos personales
  - docs/core_negocio/dominio_actores.md
"""
import pytest
from pydantic import ValidationError

from app.exceptions import UsuarioNoEncontradoError
from app.schemas.datos_personales_usuario import DatosPersonalesUsuarioSchema
from app.schemas.usuario import RegistroUsuarioSchema
from app.services.datos_personales_usuario import registrar_datos_personales
from app.services.usuario import crear_usuario


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 y CA2 — Registro exitoso de datos personales y documentación
#
#  CA1:
#  "Dado que una cuenta creada y soy un usuario nuevo, cuando cargo mi DNI,
#   nombre, apellido, entonces mis datos personales quedan registrados
#   en la plataforma."
#
#  CA2:
#  "Dado que tengo una cuenta creada, cuando subo una foto del frente y dorso
#   de mi DNI, entonces la documentación queda registrada."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1CA2_RegistroDatosPersonales:
    """
    Verifica el happy path de la US 1U a nivel servicio.

    Precondición:
        Existe una cuenta creada previamente por la US 5U.

    Resultado esperado:
        Se registran los datos personales y la documentación del usuario.
    """

    def test_registra_datos_personales_y_documentacion_para_usuario_con_cuenta_creada(
        self,
        db_session,
    ):
        """
        El servicio debe asociar a un Usuario existente:
          - DNI, nombre y apellido.
          - Foto frente y dorso del DNI.
          - Estado inicial de validación pendiente.
        """
        usuario = crear_usuario(
            db=db_session,
            schema=RegistroUsuarioSchema(
                email="datos.personales@autospot.com",
                password="password123",
            ),
        )

        payload = DatosPersonalesUsuarioSchema(
            dni="12345678",
            nombre="Mateo",
            apellido="Gomez",
            foto_dni_frente_url="uploads/dni/12345678/frente.jpg",
            foto_dni_dorso_url="uploads/dni/12345678/dorso.jpg",
        )

        datos_personales = registrar_datos_personales(
            db=db_session,
            usuario_id=usuario.id,
            schema=payload,
        )

        # CA1 — Datos personales registrados
        assert datos_personales.id is not None
        assert datos_personales.usuario_id == usuario.id
        assert datos_personales.dni == "12345678"
        assert datos_personales.nombre == "Mateo"
        assert datos_personales.apellido == "Gomez"

        # CA2 — Documentación registrada
        assert datos_personales.foto_dni_frente_url == "uploads/dni/12345678/frente.jpg"
        assert datos_personales.foto_dni_dorso_url == "uploads/dni/12345678/dorso.jpg"

        # Estado inicial para futura auditoría documental
        assert datos_personales.estado_validacion == "PENDIENTE_VALIDACION"


# ══════════════════════════════════════════════════════════════════════════════
#  CA3 — Campo obligatorio omitido o inválido
#
#  "Dado que tengo una cuenta creada, cuando intento guardar los datos
#   personales con un campo obligatorio omitido o inválido, entonces el registro
#   no se realiza y se informa que faltan campos o hay campos incorrectos."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA3_CamposObligatorios:
    """
    Verifica que el schema rechaza campos obligatorios vacíos u omitidos.

    Esta validación ocurre antes de llegar al servicio, por lo tanto evita que
    se registre documentación personal incompleta.
    """

    PAYLOAD_VALIDO = {
        "dni": "12345678",
        "nombre": "Mateo",
        "apellido": "Gomez",
        "foto_dni_frente_url": "uploads/dni/12345678/frente.jpg",
        "foto_dni_dorso_url": "uploads/dni/12345678/dorso.jpg",
    }

    def _assert_error_campo_obligatorio(self, payload: dict) -> None:
        """
        Helper: verifica que Pydantic rechaza el payload con el mensaje canónico.
        """
        with pytest.raises(ValidationError) as exc_info:
            DatosPersonalesUsuarioSchema(**payload)

        mensajes = [e["msg"] for e in exc_info.value.errors()]
        assert any("Campo obligatorio" in msg for msg in mensajes), (
            f"Se esperaba 'Campo obligatorio' en los errores, "
            f"pero se recibió: {mensajes}"
        )

    def test_ca3_dni_vacio_es_invalido(self):
        """El DNI vacío no debe ser aceptado."""
        payload = {**self.PAYLOAD_VALIDO, "dni": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca3_nombre_vacio_es_invalido(self):
        """El nombre vacío no debe ser aceptado."""
        payload = {**self.PAYLOAD_VALIDO, "nombre": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca3_apellido_vacio_es_invalido(self):
        """El apellido vacío no debe ser aceptado."""
        payload = {**self.PAYLOAD_VALIDO, "apellido": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca3_foto_frente_vacia_es_invalida(self):
        """La foto del frente del DNI vacía no debe ser aceptada."""
        payload = {**self.PAYLOAD_VALIDO, "foto_dni_frente_url": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca3_foto_dorso_vacia_es_invalida(self):
        """La foto del dorso del DNI vacía no debe ser aceptada."""
        payload = {**self.PAYLOAD_VALIDO, "foto_dni_dorso_url": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca3_campo_obligatorio_omitido_es_invalido(self):
        """
        Si falta un campo obligatorio, Pydantic debe rechazar el payload.

        En este caso se omite `dni`.
        """
        payload = self.PAYLOAD_VALIDO.copy()
        payload.pop("dni")

        with pytest.raises(ValidationError) as exc_info:
            DatosPersonalesUsuarioSchema(**payload)

        errores = exc_info.value.errors()
        campos_con_error = [error["loc"][0] for error in errores]

        assert "dni" in campos_con_error


# ══════════════════════════════════════════════════════════════════════════════
#  Regla de negocio — Usuario inexistente
#
#  Para registrar datos personales debe existir previamente una cuenta creada.
#  Si el Usuario no existe, el registro no debe realizarse.
# ══════════════════════════════════════════════════════════════════════════════
class TestUsuarioInexistente:
    """
    Verifica que no se puedan registrar datos personales para un Usuario
    inexistente.
    """

    def test_no_registra_datos_personales_si_usuario_no_existe(self, db_session):
        """
        Si el usuario_id no corresponde a un Usuario existente, el servicio
        debe lanzar una excepción de dominio.
        """
        import uuid

        payload = DatosPersonalesUsuarioSchema(
            dni="12345678",
            nombre="Mateo",
            apellido="Gomez",
            foto_dni_frente_url="uploads/dni/12345678/frente.jpg",
            foto_dni_dorso_url="uploads/dni/12345678/dorso.jpg",
        )

        usuario_id_inexistente = uuid.uuid4()

        with pytest.raises(UsuarioNoEncontradoError) as exc_info:
            registrar_datos_personales(
                db=db_session,
                usuario_id=usuario_id_inexistente,
                schema=payload,
            )

        assert str(exc_info.value) == "Usuario no encontrado"

