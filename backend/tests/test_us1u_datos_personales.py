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
  └─────┴──────────────────────────────────────────────────────────────────┘

Pendiente:
  CA3 │ Campo obligatorio omitido o inválido → no registra e informa error.

Referencias:
  - Backlog Sprint 1 — US 1U Registro datos personales
  - docs/core_negocio/dominio_actores.md
"""
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
