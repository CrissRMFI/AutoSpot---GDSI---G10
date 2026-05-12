"""
Tests unitarios para la lógica de negocio de Inicio de Sesión (US 2U).
Capa: Servicios
"""
import pytest

from app.exceptions import CredencialesInvalidasError
from app.schemas.usuario import UsuarioLogin, RegistroUsuarioSchema
from app.services.usuario import crear_usuario, autenticar_usuario


def test_autenticar_usuario_exito(db_session):
    """
    CA 1: Dado que un usuario posee una cuenta registrada,
    cuando proporciona sus credenciales de acceso correctas,
    entonces el sistema debe verificar la autenticidad y retornar el usuario.
    """
    # Setup: Crear un usuario
    schema_registro = RegistroUsuarioSchema(
        email="test_login@test.com", password="Password123!"
    )
    crear_usuario(db_session, schema_registro)

    # Acción: Autenticar
    schema_login = UsuarioLogin(
        email="test_login@test.com", password="Password123!"
    )
    usuario_autenticado = autenticar_usuario(db_session, schema_login)

    # Verificación
    assert usuario_autenticado is not None
    assert usuario_autenticado.email == "test_login@test.com"


def test_autenticar_usuario_email_inexistente(db_session):
    """
    CA 2: Dado que se ingresan credenciales erróneas (email no existe),
    entonces debe denegar la entrada mediante un mensaje genérico.
    """
    schema_login = UsuarioLogin(
        email="noexiste@test.com", password="Password123!"
    )

    with pytest.raises(CredencialesInvalidasError) as exc_info:
        autenticar_usuario(db_session, schema_login)

    assert str(exc_info.value) == "Credenciales incorrectas"


def test_autenticar_usuario_password_incorrecto(db_session):
    """
    CA 2: Dado que se ingresan credenciales erróneas (password incorrecto),
    entonces debe denegar la entrada mediante el mismo mensaje genérico.
    """
    # Setup: Crear un usuario
    schema_registro = RegistroUsuarioSchema(
        email="test_login2@test.com", password="Password123!"
    )
    crear_usuario(db_session, schema_registro)

    # Acción: Autenticar con clave mala
    schema_login = UsuarioLogin(
        email="test_login2@test.com", password="MalaPassword1!"
    )

    with pytest.raises(CredencialesInvalidasError) as exc_info:
        autenticar_usuario(db_session, schema_login)

    assert str(exc_info.value) == "Credenciales incorrectas"
