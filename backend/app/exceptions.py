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

class CredencialesInvalidasError(AutoSpotError):
    """
    Se lanza cuando el intento de inicio de sesión falla por email o contraseña incorrectos.
    Mensaje genérico para no revelar información sobre la existencia de la cuenta (CA 2).
    Mensaje canónico: "Credenciales incorrectas"
    """
    def __init__(self) -> None:
        super().__init__("Credenciales incorrectas")
