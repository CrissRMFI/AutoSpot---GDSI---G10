"""
Servicio de negocio — US 1U: Registro datos personales.

Responsabilidades de esta capa:
    1. Verificar que el Usuario exista.
    2. Registrar DNI, nombre y apellido.
    3. Registrar foto frente y dorso del DNI.
    4. Persistir los datos personales asociados al Usuario.
    5. Dejar estado inicial de validación en PENDIENTE_VALIDACION.

Esta capa NO valida campos obligatorios vacíos;
esa responsabilidad pertenece al schema Pydantic.
"""
import uuid

from sqlalchemy.orm import Session

from app.exceptions import DatosPersonalesYaRegistradosError, UsuarioNoEncontradoError, DatosPersonalesNoRegistradosError, DniYaRegistradoError
from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.models.usuario import Usuario
from app.schemas.datos_personales_usuario import DatosPersonalesUsuarioSchema


def registrar_datos_personales(
    db: Session,
    usuario_id: uuid.UUID,
    schema: DatosPersonalesUsuarioSchema,
) -> DatosPersonalesUsuario:
    """
    Registra los datos personales de un Usuario existente.

    Flujo:
        1. Verifica que exista el Usuario base creado previamente.
        2. Crea un registro de DatosPersonalesUsuario asociado.
        3. Persiste el registro y lo retorna hidratado.

    Args:
        db         : Sesión SQLAlchemy activa.
        usuario_id : UUID del Usuario existente.
        schema     : Payload ya validado por DatosPersonalesUsuarioSchema.

    Returns:
        DatosPersonalesUsuario persistido.

    Raises:
        UsuarioNoEncontradoError: Si el Usuario no existe.
        DatosPersonalesYaRegistradosError: Si el Usuario ya registró sus datos.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise UsuarioNoEncontradoError()

    datos_existentes = (
        db.query(DatosPersonalesUsuario)
        .filter(DatosPersonalesUsuario.usuario_id == usuario_id)
        .first()
    )
    if datos_existentes is not None:
        raise DatosPersonalesYaRegistradosError()

    dni_existente = (
        db.query(DatosPersonalesUsuario)
        .filter(DatosPersonalesUsuario.dni == schema.dni)
        .first()
    )
    if dni_existente is not None:
        raise DniYaRegistradoError()

    datos_personales = DatosPersonalesUsuario(
        usuario_id=usuario_id,
        dni=schema.dni,
        nombre=schema.nombre,
        apellido=schema.apellido,
        foto_dni_frente_url=schema.foto_dni_frente_url,
        foto_dni_dorso_url=schema.foto_dni_dorso_url,
    )

    db.add(datos_personales)
    db.commit()
    db.refresh(datos_personales)

    return datos_personales

def obtener_datos_personales(
    db: Session,
    usuario_id: uuid.UUID,
) -> DatosPersonalesUsuario:
    """
    Retorna los datos personales de un Usuario existente.

    Raises:
        UsuarioNoEncontradoError: Si el Usuario no existe.
        DatosPersonalesNoRegistradosError: Si el Usuario no ha cargado datos aún.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise UsuarioNoEncontradoError()

    datos_personales = (
        db.query(DatosPersonalesUsuario)
        .filter(DatosPersonalesUsuario.usuario_id == usuario_id)
        .first()
    )
    if datos_personales is None:
        raise DatosPersonalesNoRegistradosError("Datos personales no registrados")

    return datos_personales


def actualizar_datos_personales(
    db: Session,
    usuario_id: uuid.UUID,
    schema: DatosPersonalesUsuarioSchema,
) -> DatosPersonalesUsuario:
    """
    Actualiza los datos personales de un Usuario existente.

    Flujo:
        1. Verifica que exista el Usuario base creado previamente.
        2. Verifica que existan datos personales previos para ese Usuario.
        3. Actualiza el registro de DatosPersonalesUsuario asociado.
        4. Persiste los cambios y retorna el registro hidratado.

    Args:
        db         : Sesión SQLAlchemy activa.
        usuario_id : UUID del Usuario existente.
        schema     : Payload ya validado por DatosPersonalesUsuarioSchema.

    Returns:
        DatosPersonalesUsuario actualizado.

    Raises:
        UsuarioNoEncontradoError: Si el Usuario no existe.
        DatosPersonalesNoRegistradosError: Si el Usuario no tiene datos personales previos para actualizar.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise UsuarioNoEncontradoError()

    datos_personales = (
        db.query(DatosPersonalesUsuario)
        .filter(DatosPersonalesUsuario.usuario_id == usuario_id)
        .first()
    )
    if datos_personales is None:
        raise DatosPersonalesNoRegistradosError("No hay datos personales previos para actualizar")

    if schema.dni != datos_personales.dni:
        dni_existente = (
            db.query(DatosPersonalesUsuario)
            .filter(DatosPersonalesUsuario.dni == schema.dni)
            .first()
        )
        if dni_existente is not None:
            raise DniYaRegistradoError()

    datos_personales.dni = schema.dni
    datos_personales.nombre = schema.nombre
    datos_personales.apellido = schema.apellido
    datos_personales.foto_dni_frente_url = schema.foto_dni_frente_url
    datos_personales.foto_dni_dorso_url = schema.foto_dni_dorso_url

    db.commit()
    db.refresh(datos_personales)

    return datos_personales
