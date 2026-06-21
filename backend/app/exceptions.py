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


class DocumentacionHabilitanteYaRegistradaError(AutoSpotError):
    """
    Se lanza cuando un Conductor intenta registrar su documentación habilitante
    (licencia de conducir) pero ya posee un registro previo.

    La actualización posterior corresponde al endpoint de actualizar.
    Mensaje canónico: "Documentacion habilitante ya registrada"
    """
    def __init__(self) -> None:
        super().__init__("Documentacion habilitante ya registrada")


class DocumentacionHabilitanteNoRegistradaError(AutoSpotError):
    """
    Se lanza cuando se intenta acceder o actualizar la documentación habilitante
    de un Conductor que aún no la cargó.

    Mensaje canónico: "Documentacion habilitante no registrada"
    """
    def __init__(self) -> None:
        super().__init__("Documentacion habilitante no registrada")


class VehiculoNoEncontradoError(AutoSpotError):
    """
    Se lanza cuando se intenta operar sobre un Vehiculo inexistente.

    Aplica a historias donde una acción depende de un vehículo previamente
    registrado, como la US 5D de definición de tarifa diaria.
    Mensaje canónico: "Vehiculo no encontrado"
    """
    def __init__(self) -> None:
        super().__init__("Vehiculo no encontrado")


class FotoVehiculoNoEncontradaError(AutoSpotError):
    """
    Se lanza cuando se intenta reemplazar o consultar una foto de vehículo
    que no existe o no pertenece al vehículo indicado.
    """
    def __init__(self) -> None:
        super().__init__("Foto del vehiculo no encontrada")


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


class VehiculoNoDisponibleParaReservaError(AutoSpotError):
    """Se lanza cuando un vehículo no puede reservarse desde el catálogo."""
    def __init__(self) -> None:
        super().__init__("El vehículo no está disponible para reservar")


class ReservaActivaExistenteError(AutoSpotError):
    """Se lanza cuando ya existe una reserva activa para el vehículo."""
    def __init__(self) -> None:
        super().__init__("El vehículo ya tiene una reserva activa")


class ConductorConReservaActivaError(AutoSpotError):
    """Se lanza cuando el conductor ya posee una reserva activa en curso."""
    def __init__(self) -> None:
        super().__init__("Ya posees una reserva en curso y debes finalizarla o cancelarla antes de realizar otra")


class ReservaNoEncontradaError(AutoSpotError):
    """Se lanza cuando no existe una reserva para el código informado."""
    def __init__(self) -> None:
        super().__init__("Reserva no encontrada")


class ReservaCodigoYaVerificadoError(AutoSpotError):
    """Se lanza cuando se intenta verificar un código ya usado previamente."""
    def __init__(self) -> None:
        super().__init__("El código de reserva ya fue utilizado")


class ReservaNoRechazableError(AutoSpotError):
    """Se lanza cuando una reserva ya no puede rechazarse por su estado actual."""
    def __init__(self) -> None:
        super().__init__("La reserva no puede rechazarse en su estado actual")


class MotivoRechazoRequeridoError(AutoSpotError):
    """Se lanza cuando se rechaza una reserva sin motivo."""
    def __init__(self) -> None:
        super().__init__("Debes ingresar un motivo para rechazar la reserva")


class ReservaSinCheckinAprobadoError(AutoSpotError):
    """
    Se lanza al registrar la salida de una reserva cuyo conductor no
    completó el check-in o cuyo check-in no fue aprobado por el recepcionista.
    """
    def __init__(self, mensaje: str = "No se puede registrar la salida: el check-in del conductor no está aprobado.") -> None:
        super().__init__(mensaje)


class ReservaNoEntregableError(AutoSpotError):
    """
    Se lanza al registrar la salida de una reserva cuyo estado no lo
    permite (código sin verificar, ya entregada, finalizada, etc.).
    """
    def __init__(self, mensaje: str = "La reserva no puede entregarse en su estado actual") -> None:
        super().__init__(mensaje)


class ReservaNoEnCursoError(AutoSpotError):
    """Se lanza al registrar la entrada sin un alquiler en curso."""
    def __init__(self, mensaje: str = "No hay un alquiler en curso para ese auto") -> None:
        super().__init__(mensaje)


class CheckoutNoDisponibleError(AutoSpotError):
    """
    Se lanza al intentar completar el checkout cuando el auto todavía
    no fue reportado como devuelto en la estación.
    """
    def __init__(self) -> None:
        super().__init__(
            "El formulario de checkout no está disponible: el auto aún no fue "
            "devuelto en la estación."
        )


class CheckoutYaRegistradoError(AutoSpotError):
    """Se lanza cuando ya existe un checkout para la reserva."""
    def __init__(self) -> None:
        super().__init__("El checkout de esta reserva ya fue registrado")


class CheckoutNoEncontradoError(AutoSpotError):
    """Se lanza cuando un checkout no existe o no pertenece al conductor."""
    def __init__(self) -> None:
        super().__init__("Checkout no encontrado")


class CheckoutNoConfirmableError(AutoSpotError):
    """Se lanza al confirmar/rechazar un checkout que no está pendiente."""
    def __init__(self) -> None:
        super().__init__("El checkout no está pendiente de confirmación")


class DocumentacionVehiculoNoEditableError(AutoSpotError):
    """
    Se lanza cuando se intenta cargar o modificar documentación de un vehículo
    cuyo estado no permite cambios documentales.
    """
    def __init__(self) -> None:
        super().__init__("La documentación del vehículo no puede modificarse en este estado")

class DocumentacionVehiculoNoExistenteError(AutoSpotError):
    """
    Se lanza cuando se intenta actualizar documentación de un vehículo
    que no tiene documentación existente.
    """
    def __init__(self) -> None:
        super().__init__("No existe documentación previa para este vehículo")

class ActualizarDocumentacionVehiculoDisponibleError(AutoSpotError):
    """
    Se lanza cuando se intenta actualizar la documentación de un vehículo
    que se encuentra disponible para alquilar, lo cual no está permitido
    para evitar inconsistencias en reservas activas.
    """
    def __init__(self) -> None:
        super().__init__("No es posible actualizar la documentación del vehículo mientras esté disponible para alquilar")

class ActualizarDocumentacionVehiculoConReservaActivaError(AutoSpotError):
    """
    Se lanza cuando se intenta actualizar la documentación de un vehículo
    que tiene una reserva activa en curso.
    """
    def __init__(self) -> None:
        super().__init__("No es posible actualizar la documentación del vehículo mientras haya una reserva activa en curso")

class MarcaNoEncontradaError(AutoSpotError):
    """Se lanza al referenciar una marca inexistente en el catálogo."""
    def __init__(self) -> None:
        super().__init__("Marca no encontrada")


class MarcaYaExistenteError(AutoSpotError):
    """Se lanza al intentar crear una marca con un nombre ya registrado."""
    def __init__(self) -> None:
        super().__init__("Marca ya existente")


class ModeloYaExistenteError(AutoSpotError):
    """Se lanza al intentar crear un modelo ya registrado para esa marca."""
    def __init__(self) -> None:
        super().__init__("Modelo ya existente para la marca")


class MarcaModeloInexistenteError(AutoSpotError):
    """
    Se lanza al registrar un vehículo con una combinación marca/modelo que
    no existe en el catálogo. Mensaje canónico mantenido para compatibilidad
    con tests previos: "Combinacion marca modelo inexistente".
    """
    def __init__(self) -> None:
        super().__init__("Combinacion marca modelo inexistente")


class SolicitudDocumentacionNoEncontradaError(AutoSpotError):
    """Se lanza cuando no existe la solicitud de documentación solicitada."""
    def __init__(self) -> None:
        super().__init__("Solicitud de documentacion no encontrada")


class TipoSolicitudDocumentacionInvalidoError(AutoSpotError):
    """Se lanza cuando el tipo de solicitud no es VEHICULO ni CONDUCTOR."""
    def __init__(self) -> None:
        super().__init__("Tipo de solicitud de documentacion invalido")


class NotificacionNoEncontradaError(AutoSpotError):
    """Se lanza cuando una notificación no existe o no pertenece al usuario."""
    def __init__(self) -> None:
        super().__init__("Notificacion no encontrada")


class ReservaNoFinalizadaError(AutoSpotError):
    """
    Se lanza al intentar valorar una reserva que no está FINALIZADA
    o que no tiene devolución física registrada.
    """
    def __init__(self) -> None:
        super().__init__(
            "Solo se puede valorar una reserva finalizada con devolución registrada"
        )


class ValoracionYaRegistradaError(AutoSpotError):
    """Se lanza al intentar registrar una segunda valoración para la misma reserva."""
    def __init__(self) -> None:
        super().__init__("Ya existe una valoración para esta reserva")


class TestimonioYaRegistradoError(AutoSpotError):
    """
    Se lanza al intentar registrar un segundo testimonio para la misma reserva.

    Corresponde al CA 3 de la US 18C: inmutabilidad y transparencia de reseñas.
    Mensaje canónico: "Ya existe un testimonio para esta reserva"
    """
    def __init__(self) -> None:
        super().__init__("Ya existe un testimonio para esta reserva")


class ReservaNoFinalizadaParaTestimonioError(AutoSpotError):
    """
    Se lanza al intentar dejar un testimonio sobre una reserva que no está
    en estado FINALIZADA con cierre administrativo (CA 1 US 18C).
    """
    def __init__(self) -> None:
        super().__init__(
            "Solo se puede dejar un testimonio sobre una contratación cerrada administrativamente"
        )


# ── Reportes de falla critica ────────────────────────────────────────────────

class ReporteDuplicadoError(AutoSpotError):
    """Se lanza cuando ya existe un reporte para la reserva indicada."""
    def __init__(self) -> None:
        super().__init__("Ya existe un reporte de incidencia para esta reserva")


class ReporteNoEncontradoError(AutoSpotError):
    """Se lanza cuando un reporte no existe."""
    def __init__(self) -> None:
        super().__init__("Reporte no encontrado")


class ReporteNoResolubleError(AutoSpotError):
    """Se lanza al intentar resolver un reporte que no está ACTIVO."""
    def __init__(self) -> None:
        super().__init__("El reporte no puede resolverse en su estado actual")


class ReporteFotosRequeridasError(AutoSpotError):
    """Se lanza cuando un reporte se intenta crear sin fotos válidas."""
    def __init__(self) -> None:
        super().__init__("El reporte requiere al menos una foto")


class ReporteFotoDescripcionRequeridaError(AutoSpotError):
    """Se lanza cuando una foto del reporte no tiene descripción."""
    def __init__(self) -> None:
        super().__init__("Cada foto del reporte requiere una descripción")


class ReporteNoPerteneceAPropietarioError(AutoSpotError):
    """Se lanza cuando un usuario sin permiso intenta resolver un reporte."""
    def __init__(self) -> None:
        super().__init__("No tenés permiso para resolver este reporte")


class VehiculoConReporteActivoError(AutoSpotError):
    """Se lanza al intentar habilitar la disponibilidad de un vehículo con reporte activo."""
    def __init__(self) -> None:
        super().__init__(
            "No es posible marcar el vehiculo como disponible mientras tenga un "
            "reporte critico activo"
        )
