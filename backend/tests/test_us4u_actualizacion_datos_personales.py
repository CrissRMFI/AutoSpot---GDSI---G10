import pytest

from app.exceptions import MailExistenteError
from app.schemas.datos_personales_usuario import DatosPersonalesUsuarioSchema
from app.schemas.usuario import RegistroUsuarioSchema
from app.services.datos_personales_usuario import registrar_datos_personales, actualizar_datos_personales
from app.services.usuario import actualizar_usuario, crear_usuario

def setup_usuario_con_datos_personales(db_session):
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

    registrar_datos_personales(
        db=db_session,
        usuario_id=usuario.id,
        schema=payload,
    )
    return usuario

class TestCA1_ActualizarDatosPersonalesNoCriticos:
    """
    Verifica la actualización exitosa de datos personales no criticos.

    Precondición:
        Existe una cuenta creada previamente por la US 5U y datos cargados por la US 1U.

    Resultado esperado:
        Se actualizan los datos personales del usuario.
    """

    def test_actualiza_datos_personales_para_usuario_con_cuenta_creada(
        self,
        db_session,
    ):
        """
        El servicio debe asociar a un Usuario existente:
          - DNI, nombre y apellido.
          - Foto frente y dorso del DNI.
          - Estado inicial de validación pendiente.
        """
        usuario = setup_usuario_con_datos_personales(db_session)

        actualizacion = DatosPersonalesUsuarioSchema(
            dni="87654321",
            nombre="Pedro",
            apellido="Suarez",
            foto_dni_frente_url="uploads/dni/87654321/frente.jpg",
            foto_dni_dorso_url="uploads/dni/87654321/dorso.jpg",
        )

        datos_personales_actualizados =  actualizar_datos_personales(
            db=db_session,
            usuario_id=usuario.id,
            schema=actualizacion,
        )
        #CA1: Verificar que los datos personales no criticos se actualizan correctamente
        assert datos_personales_actualizados.dni == "87654321"
        assert datos_personales_actualizados.nombre == "Pedro"
        assert datos_personales_actualizados.apellido == "Suarez"
        assert datos_personales_actualizados.foto_dni_frente_url == "uploads/dni/87654321/frente.jpg"
        assert datos_personales_actualizados.foto_dni_dorso_url == "uploads/dni/87654321/dorso.jpg"

class TestCA2_CambioACrontraseñaInvalida:
    """
    Verifica que el sistema rechaza la actualización de contraseña con una contraseña inválida.

    Precondición:
        Existe una cuenta creada previamente por la US 5U y datos cargados por la US 1U.

    Resultado esperado:
        El sistema lanza un error de validación al intentar actualizar con una contraseña inválida.
    """

    def test_rechaza_actualizacion_con_contraseña_invalida(
        self,
        db_session,
    ):
        usuario = setup_usuario_con_datos_personales(db_session)

        
        with pytest.raises(ValueError) as exc_info:
            actualizacion = RegistroUsuarioSchema(
            email="datos.personales@autospot.com",
            password="short",  # Contraseña inválida (menos de 8 caracteres)
        )


class TestCA3_CambioIdentificadoresUnicos:
    """
    Verifica que el sistema rechaza la actualización de datos personales
    con identificadores únicos que ya existen en otro registro.

    Precondición:
        Existen al menos dos cuentas creadas previamente por la US 5U y datos cargados por la US 1U.

    Resultado esperado:
        El sistema lanza un error de validación al intentar actualizar con un email ya registrado.
    """

    def test_rechaza_actualizacion_con_email_duplicado(
        self,
        db_session,
    ):
        usuario1 = setup_usuario_con_datos_personales(db_session)
        usuario2 = crear_usuario(
            db=db_session,
            schema=RegistroUsuarioSchema(
                email="datos.personales2@autospot.com",
                password="password123",
            ),
        )

        actualizacion = RegistroUsuarioSchema(
            email="datos.personales2@autospot.com",  # Email ya registrado por usuario2
            password="password123",
        )
        

        with pytest.raises(MailExistenteError) as exc_info:
            actualizar_usuario(
                db=db_session,
                usuario_id=usuario1.id,
                schema=actualizacion,
            )