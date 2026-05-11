"""
Excepciones de dominio de AutoSpot.

Se definen aquí para centralizar los errores de negocio
y desacoplarlos de la capa HTTP (FastAPI) y de la capa de datos.
"""


class AutoSpotError(Exception):
    """Base para todas las excepciones de dominio de AutoSpot."""
    pass


class MailExistenteError(AutoSpotError):
    """
    Se lanza cuando se intenta registrar un email que ya existe en la plataforma.

    Corresponde al CA 5 de la US 5U.
    Mensaje canónico: "Mail existente"
    """
    def __init__(self) -> None:
        super().__init__("Mail existente")


class UsuarioNoEncontradoError(AutoSpotError):
    """
    Se lanza cuando se intenta operar sobre un Usuario inexistente.

    Aplica a historias donde una acción depende de una cuenta previamente creada,
    como la US 1U de registro de datos personales.
    Mensaje canónico: "Usuario no encontrado"
    """
    def __init__(self) -> None:
        super().__init__("Usuario no encontrado")

