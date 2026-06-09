"""
Tests Unitarios — US 1C: Cargar identidad y documentación habilitante.

Criterios de Aceptación cubiertos a nivel servicio/schema:
  ┌─────┬──────────────────────────────────────────────────────────────────┐
  │ CA  │ Descripción                                                      │
  ├─────┼──────────────────────────────────────────────────────────────────┤
  │ CA1 │ Cuenta creada + carga categoria y fechas de la licencia          │
  │ CA2 │ Cuenta creada + sube foto frente y dorso de la licencia          │
  │ CA3 │ Campos vacíos o fechas inconsistentes → registro rechazado       │
  │ CA4 │ Documentación ya registrada → segundo registro rechazado         │
  │ CA5 │ Actualización conserva la asociación con el Conductor            │
  └─────┴──────────────────────────────────────────────────────────────────┘
"""
import uuid
from datetime import date

import pytest
from pydantic import ValidationError

from app.exceptions import (
    DocumentacionHabilitanteNoRegistradaError,
    DocumentacionHabilitanteYaRegistradaError,
    UsuarioNoEncontradoError,
)
from app.schemas.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductorSchema,
)
from app.schemas.usuario import RegistroUsuarioSchema
from app.services.documentacion_habilitante_conductor import (
    actualizar_documentacion_habilitante,
    obtener_documentacion_habilitante,
    registrar_documentacion_habilitante,
)
from app.services.usuario import crear_usuario


PAYLOAD_VALIDO = {
    "categoria": "B1",
    "fecha_emision": date(2024, 1, 10),
    "fecha_vencimiento": date(2029, 1, 10),
    "foto_licencia_frente_url": "uploads/licencia/12345678/frente.jpg",
    "foto_licencia_dorso_url": "uploads/licencia/12345678/dorso.jpg",
}


def _crear_usuario_de_prueba(db_session, email: str = "conductor@autospot.com"):
    return crear_usuario(
        db=db_session,
        schema=RegistroUsuarioSchema(email=email, password="password123"),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 y CA2 — Registro exitoso de documentación habilitante
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1CA2_RegistroDocumentacionHabilitante:
    def test_registra_licencia_y_fotos_para_conductor_con_cuenta_creada(
        self, db_session
    ):
        usuario = _crear_usuario_de_prueba(db_session)
        payload = DocumentacionHabilitanteConductorSchema(**PAYLOAD_VALIDO)

        documentacion = registrar_documentacion_habilitante(
            db=db_session,
            usuario_id=usuario.id,
            schema=payload,
        )

        # CA1 — Datos de la licencia
        assert documentacion.id is not None
        assert documentacion.usuario_id == usuario.id
        assert documentacion.categoria == "B1"
        assert documentacion.fecha_emision == date(2024, 1, 10)
        assert documentacion.fecha_vencimiento == date(2029, 1, 10)

        # CA2 — Fotos registradas
        assert documentacion.foto_licencia_frente_url == (
            "uploads/licencia/12345678/frente.jpg"
        )
        assert documentacion.foto_licencia_dorso_url == (
            "uploads/licencia/12345678/dorso.jpg"
        )

        # Estado inicial documental
        assert documentacion.estado_validacion == "PENDIENTE_REVISION"


# ══════════════════════════════════════════════════════════════════════════════
#  CA3 — Campos obligatorios y fechas inconsistentes
# ══════════════════════════════════════════════════════════════════════════════
class TestCA3_ValidacionPayload:
    def _assert_error_validacion(self, payload: dict, mensaje_esperado: str) -> None:
        with pytest.raises(ValidationError) as exc_info:
            DocumentacionHabilitanteConductorSchema(**payload)

        mensajes = [e["msg"] for e in exc_info.value.errors()]
        assert any(mensaje_esperado in msg for msg in mensajes), (
            f"Se esperaba '{mensaje_esperado}' en los errores, "
            f"pero se recibió: {mensajes}"
        )

    def test_foto_frente_vacia_es_invalida(self):
        self._assert_error_validacion(
            {**PAYLOAD_VALIDO, "foto_licencia_frente_url": ""},
            "Campo obligatorio",
        )

    def test_foto_dorso_vacia_es_invalida(self):
        self._assert_error_validacion(
            {**PAYLOAD_VALIDO, "foto_licencia_dorso_url": ""},
            "Campo obligatorio",
        )

    def test_categoria_no_permitida_es_invalida(self):
        self._assert_error_validacion(
            {**PAYLOAD_VALIDO, "categoria": "Z"},
            "Categoria invalida",
        )

    def test_fecha_vencimiento_anterior_a_emision_es_invalida(self):
        self._assert_error_validacion(
            {
                **PAYLOAD_VALIDO,
                "fecha_emision": date(2029, 1, 10),
                "fecha_vencimiento": date(2024, 1, 10),
            },
            "fecha de vencimiento debe ser posterior",
        )

    def test_fecha_vencimiento_igual_a_emision_es_invalida(self):
        self._assert_error_validacion(
            {
                **PAYLOAD_VALIDO,
                "fecha_emision": date(2024, 1, 10),
                "fecha_vencimiento": date(2024, 1, 10),
            },
            "fecha de vencimiento debe ser posterior",
        )

    def test_campo_obligatorio_omitido_es_invalido(self):
        payload = PAYLOAD_VALIDO.copy()
        payload.pop("foto_licencia_frente_url")

        with pytest.raises(ValidationError) as exc_info:
            DocumentacionHabilitanteConductorSchema(**payload)

        campos_con_error = [error["loc"][0] for error in exc_info.value.errors()]
        assert "foto_licencia_frente_url" in campos_con_error


# ══════════════════════════════════════════════════════════════════════════════
#  Reglas de negocio — Usuario inexistente y registros duplicados
# ══════════════════════════════════════════════════════════════════════════════
class TestUsuarioInexistente:
    def test_no_registra_si_usuario_no_existe(self, db_session):
        payload = DocumentacionHabilitanteConductorSchema(**PAYLOAD_VALIDO)

        with pytest.raises(UsuarioNoEncontradoError) as exc_info:
            registrar_documentacion_habilitante(
                db=db_session,
                usuario_id=uuid.uuid4(),
                schema=payload,
            )

        assert str(exc_info.value) == "Usuario no encontrado"


class TestCA4_DocumentacionYaRegistrada:
    def test_no_permite_registrar_dos_veces_para_mismo_conductor(self, db_session):
        usuario = _crear_usuario_de_prueba(
            db_session,
            email="conductor.duplicado@autospot.com",
        )

        payload = DocumentacionHabilitanteConductorSchema(**PAYLOAD_VALIDO)

        registrar_documentacion_habilitante(
            db=db_session,
            usuario_id=usuario.id,
            schema=payload,
        )

        with pytest.raises(DocumentacionHabilitanteYaRegistradaError) as exc_info:
            registrar_documentacion_habilitante(
                db=db_session,
                usuario_id=usuario.id,
                schema=payload,
            )

        assert str(exc_info.value) == "Documentacion habilitante ya registrada"


# ══════════════════════════════════════════════════════════════════════════════
#  CA5 — Actualización conserva la asociación con el Conductor
# ══════════════════════════════════════════════════════════════════════════════
class TestCA5_ActualizacionDocumentacion:
    def test_actualiza_documentacion_existente_y_mantiene_usuario_id(
        self, db_session
    ):
        usuario = _crear_usuario_de_prueba(
            db_session,
            email="conductor.update@autospot.com",
        )

        registrar_documentacion_habilitante(
            db=db_session,
            usuario_id=usuario.id,
            schema=DocumentacionHabilitanteConductorSchema(**PAYLOAD_VALIDO),
        )

        payload_actualizado = DocumentacionHabilitanteConductorSchema(
            **{
                **PAYLOAD_VALIDO,
                "categoria": "B2",
                "fecha_vencimiento": date(2031, 1, 10),
            }
        )

        documentacion_actualizada = actualizar_documentacion_habilitante(
            db=db_session,
            usuario_id=usuario.id,
            schema=payload_actualizado,
        )

        assert documentacion_actualizada.usuario_id == usuario.id
        assert documentacion_actualizada.categoria == "B2"
        assert documentacion_actualizada.fecha_vencimiento == date(2031, 1, 10)

    def test_no_actualiza_si_no_hay_documentacion_previa(self, db_session):
        usuario = _crear_usuario_de_prueba(
            db_session,
            email="conductor.sin.doc@autospot.com",
        )

        with pytest.raises(DocumentacionHabilitanteNoRegistradaError):
            actualizar_documentacion_habilitante(
                db=db_session,
                usuario_id=usuario.id,
                schema=DocumentacionHabilitanteConductorSchema(**PAYLOAD_VALIDO),
            )


# ══════════════════════════════════════════════════════════════════════════════
#  Obtener documentación habilitante
# ══════════════════════════════════════════════════════════════════════════════
class TestObtenerDocumentacion:
    def test_obtiene_documentacion_registrada(self, db_session):
        usuario = _crear_usuario_de_prueba(
            db_session,
            email="conductor.get@autospot.com",
        )

        registrar_documentacion_habilitante(
            db=db_session,
            usuario_id=usuario.id,
            schema=DocumentacionHabilitanteConductorSchema(**PAYLOAD_VALIDO),
        )

        documentacion = obtener_documentacion_habilitante(
            db=db_session,
            usuario_id=usuario.id,
        )

        assert documentacion.usuario_id == usuario.id
        assert documentacion.categoria == "B1"

    def test_lanza_excepcion_si_no_hay_documentacion(self, db_session):
        usuario = _crear_usuario_de_prueba(
            db_session,
            email="conductor.get.empty@autospot.com",
        )

        with pytest.raises(DocumentacionHabilitanteNoRegistradaError):
            obtener_documentacion_habilitante(
                db=db_session,
                usuario_id=usuario.id,
            )

# ══════════════════════════════════════════════════════════════════════════════
#  Aprobar documentación habilitante (Atajo)
# ══════════════════════════════════════════════════════════════════════════════
class TestAprobarDocumentacion:
    def test_aprueba_documentacion_registrada(self, db_session):
        usuario = _crear_usuario_de_prueba(
            db_session,
            email="conductor.aprobar@autospot.com",
        )

        registrar_documentacion_habilitante(
            db=db_session,
            usuario_id=usuario.id,
            schema=DocumentacionHabilitanteConductorSchema(**PAYLOAD_VALIDO),
        )

        from app.services.documentacion_habilitante_conductor import aprobar_documentacion_habilitante
        documentacion_aprobada = aprobar_documentacion_habilitante(
            db=db_session,
            usuario_id=usuario.id,
        )

        assert documentacion_aprobada.usuario_id == usuario.id
        assert documentacion_aprobada.estado_validacion == "APROBADO"

    def test_lanza_excepcion_si_no_hay_documentacion_para_aprobar(self, db_session):
        usuario = _crear_usuario_de_prueba(
            db_session,
            email="conductor.aprobar.empty@autospot.com",
        )

        from app.services.documentacion_habilitante_conductor import aprobar_documentacion_habilitante
        with pytest.raises(DocumentacionHabilitanteNoRegistradaError):
            aprobar_documentacion_habilitante(
                db=db_session,
                usuario_id=usuario.id,
            )
