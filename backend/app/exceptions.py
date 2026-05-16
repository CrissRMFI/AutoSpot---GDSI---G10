"""
Excepciones de dominio de AutoSpot.

Se definen aquí para centralizar los errores de negocio
y desacoplarlos de la capa HTTP (FastAPI) y de la capa de datos.
"""


class AutoSpotError(Exception):
    """Base para todas las excepciones de dominio de AutoSpot."""
    pass


class TokenInvalidoError(AutoSpotError):
    """
    Se lanza cuando un token JWT es inválido, expirado o ya fue invalidado
    por un logout previo (blacklist).

    Corresponde a los CA1 y CA2 de la US 3U.
    Mensaje canónico: "Token inválido"
    """
    def __init__(self, mensaje: str = "Token inválido") -> None:
        super().__init__(mensaje)

class MailExistenteError(AutoSpotError):
    """
    Se lanza cuando se intenta registrar un email que ya existe en la plataforma.

    Corresponde al CA 5 de la US 5U.
    Mensaje canónico: "Mail existente"
    """
    def __init__(self) -> None:
        super().__init__("Mail existente")

class MailInexistenteError(AutoSpotError):
    """
    Se lanza cuando el correo no existe en la base de datos durante el login.
    """
    def __init__(self) -> None:
        super().__init__("Email inexistente")

class ContraseniaIncorrectaError(AutoSpotError):
    """
    Se lanza cuando el correo existe pero la contraseña no coincide.
    """
    def __init__(self) -> None:
        super().__init__("Contraseña incorrecta")
  
        
class UsuarioNoEncontradoError(AutoSpotError):
    """
    Se lanza cuando se intenta operar sobre un Usuario inexistente.

    Aplica a historias donde una acción depende de una cuenta previamente creada,
    como la US 1U de registro de datos personales.
    Mensaje canónico: "Usuario no encontrado"
    """
    def __init__(self) -> None:
        super().__init__("Usuario no encontrado")


class DatosPersonalesYaRegistradosError(AutoSpotError):
    """
    Se lanza cuando se intenta registrar datos personales para un Usuario
    que ya posee un registro de documentación personal.

    La US 1U cubre el registro inicial; la actualización posterior corresponde
    a la US 4U de gestión y actualización de perfil.
    Mensaje canónico: "Datos personales ya registrados"
    """
    def __init__(self) -> None:
        super().__init__("Datos personales ya registrados")

class DniYaRegistradoError(AutoSpotError):
    """
    Se lanza cuando se intenta registrar un DNI que ya se encuentra
    asociado a otro usuario en el sistema.
    """
    def __init__(self) -> None:
        super().__init__("El DNI ya se encuentra registrado por otro usuario")

class DatosPersonalesNoRegistradosError(AutoSpotError):
    """
    Se lanza cuando se intenta acceder a datos personales de un Usuario
    que no ha registrado su documentación personal.

    La US 4U cubre la actualizacion de los datos personales, el registro
    inicial corresponde a la US 1U.
    Mensaje canónico: "Datos personales no registrados"
    """
    def __init__(self) -> None:
        super().__init__("Datos personales no registrados")


class VehiculoNoEncontradoError(AutoSpotError):
    """
    Se lanza cuando se intenta operar sobre un Vehiculo inexistente.

    Aplica a historias donde una acción depende de un vehículo previamente
    registrado, como la US 5D de definición de tarifa diaria.
    Mensaje canónico: "Vehiculo no encontrado"
    """
    def __init__(self) -> None:
        super().__init__("Vehiculo no encontrado")


class VehiculoNoHabilitadoError(AutoSpotError):
    """
    Se lanza cuando se intenta cambiar la disponibilidad de un auto que
    todavía no fue habilitado.
    """
    def __init__(self) -> None:
        super().__init__("El auto aún no fue habilitado")


class VehiculoConReservaActivaError(AutoSpotError):
    """
    Se lanza cuando se intenta deshabilitar un auto que tiene alquileres
    o reservas en curso.
    """
    def __init__(self) -> None:
        super().__init__("No es posible deshabilitar el auto mientras haya una reserva o alquiler en curso")

