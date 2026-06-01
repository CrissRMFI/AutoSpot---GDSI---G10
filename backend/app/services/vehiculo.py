"""
Servicio de negocio — US 1D: Cargar características y fotos del auto.

Responsabilidades de esta capa:
    1. Verificar que el propietario exista como Usuario base.
    2. Registrar características obligatorias del vehículo.
    3. Registrar fotos asociadas.
    4. Persistir el vehículo con estado inicial PENDIENTE_DOCUMENTACION.

Esta capa NO valida campos obligatorios, año, formato o cantidad de fotos;
esas responsabilidades pertenecen al schema Pydantic.
"""
import uuid
from sqlalchemy.orm import Session

from app.exceptions import (
    DocumentacionVehiculoNoEditableError,
    FotoVehiculoNoEncontradaError,
    MarcaModeloInexistenteError,
    UsuarioNoEncontradoError,
    VehiculoNoEncontradoError,
    VehiculoNoHabilitadoError,
    VehiculoConReservaActivaError,
)
from app.models.foto_vehiculo import FotoVehiculo
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo import (
    DocumentacionVehiculoSchema,
    RegistroVehiculoSchema,
    ActualizarVehiculoPayloadSchema,
)
from app.services.marca_service import validar_combo_marca_modelo
from app.services.notificacion import (
    cerrar_notificacion_documentacion_pendiente,
    crear_notificacion_documentacion_pendiente,
)


ESTADOS_DOCUMENTACION_EDITABLE = {"PENDIENTE_DOCUMENTACION", "RECHAZADO"}
ESTADO_DOCUMENTACION_CORREGIBLE = "RECHAZADO"
CAMBIOS_DOCUMENTALES_ACTUALIZACION = (
    "patente",
    "chasis",
    "motor",
    "titular",
    "estacion",
    "telefono",
)
ESTADOS_RESERVA_QUE_BLOQUEAN_DISPONIBILIDAD = {
    "CONFIRMADA",
    "CODIGO_GENERADO",
    "VERIFICADA",
    "EN_CURSO",
    "ENTREGA_SOLICITADA",
    "DEVUELTO",
    "CHECKOUT_PENDIENTE",
}

def registrar_vehiculo(db: Session, schema: RegistroVehiculoSchema) -> Vehiculo:
    """
    Registra un vehículo con sus características y fotos.

    Flujo:
        1. Verifica que exista el Usuario propietario.
        2. Crea el Vehiculo con estado inicial PENDIENTE_DOCUMENTACION.
        3. Crea las FotoVehiculo asociadas.
        4. Persiste y retorna el Vehiculo hidratado.

    Args:
        db     : Sesión SQLAlchemy activa.
        schema : Payload ya validado por RegistroVehiculoSchema.

    Returns:
        Vehiculo persistido con sus fotos asociadas.

    Raises:
        UsuarioNoEncontradoError: Si el propietario no existe.
        MarcaModeloInexistenteError: Si la combinación marca/modelo no está
            registrada en el catálogo (tablas `marcas`/`modelos`).
    """
    propietario = (
        db.query(Usuario)
        .filter(Usuario.id == schema.propietario_id)
        .first()
    )
    if propietario is None:
        raise UsuarioNoEncontradoError()

    validar_combo_marca_modelo(db, marca=schema.marca, modelo=schema.modelo)

    vehiculo = Vehiculo(
      propietario_id=schema.propietario_id,
      marca=schema.marca,
      modelo=schema.modelo,
      anio=schema.anio,
      tipo_transmision=schema.tipo_transmision,
      capacidad=schema.capacidad,
      categoria=schema.categoria,
      tipo_combustible=schema.tipo_combustible,
      pets_friendly=schema.pets_friendly,
    )

    vehiculo.fotos = [
        FotoVehiculo(
            lado=foto.lado,
            url=foto.url,
            formato=foto.formato,
            tamanio_bytes=foto.tamanio_bytes,
        )
        for foto in schema.fotos
    ]

    db.add(vehiculo)
    db.flush()
    crear_notificacion_documentacion_pendiente(db=db, vehiculo=vehiculo)
    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def actualizar_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    schema: ActualizarVehiculoPayloadSchema
) -> Vehiculo:
    """
    Actualiza las características y fotos de un vehículo.
    No actualiza marca ni modelo para mantener integridad con reservas/reglas de negocio.
    Reemplaza todas las fotos por las nuevas provistas.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    cambios_documentales = any(
        getattr(schema, campo) is not None
        and getattr(schema, campo) != getattr(vehiculo, campo)
        for campo in CAMBIOS_DOCUMENTALES_ACTUALIZACION
    )
    if (
        cambios_documentales
        and vehiculo.estado_registro != ESTADO_DOCUMENTACION_CORREGIBLE
    ):
        raise DocumentacionVehiculoNoEditableError()

    # Se actualizan las características generales, ignorando marca y modelo
    vehiculo.anio = schema.anio
    vehiculo.tipo_transmision = schema.tipo_transmision
    vehiculo.capacidad = schema.capacidad
    vehiculo.categoria = schema.categoria
    vehiculo.tipo_combustible = schema.tipo_combustible
    vehiculo.pets_friendly = schema.pets_friendly

    # Actualizar campos de documentación opcionales
    if schema.patente is not None: vehiculo.patente = schema.patente
    if schema.chasis is not None: vehiculo.chasis = schema.chasis
    if schema.motor is not None: vehiculo.motor = schema.motor
    if schema.titular is not None: vehiculo.titular = schema.titular
    if schema.estacion is not None: vehiculo.estacion = schema.estacion
    if schema.telefono is not None: vehiculo.telefono = schema.telefono

    # Reemplazar fotos (debido a cascade delete-orphan, las viejas se borran)
    vehiculo.fotos = [
        FotoVehiculo(
            lado=foto.lado,
            url=foto.url,
            formato=foto.formato,
            tamanio_bytes=foto.tamanio_bytes,
        )
        for foto in schema.fotos
    ]

    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def definir_precio_vehiculo(
    db: Session,
    vehiculo_id,
    precio_por_dia,
) -> Vehiculo:
    """
    Define la tarifa diaria de un vehículo existente.

    US 5D — Alcance actual:
        - guarda precio por día
        - sin descuentos
        - sin comisión
        - sin precio dinámico
        - sin moneda múltiple

    Args:
        db             : Sesión SQLAlchemy activa.
        vehiculo_id    : Identificador del vehículo.
        precio_por_dia : Tarifa diaria validada por capas superiores.

    Returns:
        Vehiculo actualizado.

    Nota:
        La validación de vehículo inexistente se completará en el siguiente
        bloque de TDD con una excepción de dominio específica.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    vehiculo.precio_por_dia = precio_por_dia

    db.commit()
    db.refresh(vehiculo)

    return vehiculo

def obtener_vehiculo(db: Session, vehiculo_id: uuid.UUID) -> Vehiculo:
    """
    Obtiene un vehículo por su ID.

    Args:
        db: Sesión SQLAlchemy.
        vehiculo_id: UUID del vehículo.

    Returns:
        Vehiculo: El vehículo si existe.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    return vehiculo

def agregar_foto_a_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    lado: str,
    url: str,
    formato: str,
    tamanio_bytes: int,
) -> FotoVehiculo:
    """
    Agrega una foto adicional a un vehículo existente.

    Pensado para fotos del lado EXTRA cargadas después del alta inicial,
    aunque admite cualquier lado válido.

    Args:
        db            : Sesión SQLAlchemy activa.
        vehiculo_id   : UUID del vehículo.
        lado          : Lado de la foto (FRENTE/TRASERA/...EXTRA).
        url           : URL pública devuelta por Cloudinary.
        formato       : Formato del archivo (jpg/jpeg/png/webp).
        tamanio_bytes : Tamaño del archivo subido en bytes.

    Returns:
        La FotoVehiculo persistida.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )
    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    foto = FotoVehiculo(
        vehiculo_id=vehiculo_id,
        lado=lado,
        url=url,
        formato=formato,
        tamanio_bytes=tamanio_bytes,
    )

    db.add(foto)
    db.commit()
    db.refresh(foto)

    return foto


def reemplazar_foto_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    foto_id: uuid.UUID,
    url: str,
    formato: str,
    tamanio_bytes: int,
) -> FotoVehiculo:
    """
    Reemplaza la URL y metadata de una foto existente de un vehículo.

    El cliente sube primero la imagen nueva a Cloudinary (manteniendo el
    `lado` original) y luego invoca este servicio para persistir la nueva
    URL en la foto ya asociada al vehículo.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
        FotoVehiculoNoEncontradaError: Si la foto no existe o no pertenece
            al vehículo indicado.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )
    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    foto = (
        db.query(FotoVehiculo)
        .filter(
            FotoVehiculo.id == foto_id,
            FotoVehiculo.vehiculo_id == vehiculo_id,
        )
        .first()
    )
    if foto is None:
        raise FotoVehiculoNoEncontradaError()

    foto.url = url
    foto.formato = formato
    foto.tamanio_bytes = tamanio_bytes

    db.commit()
    db.refresh(foto)

    return foto


def listar_vehiculos_por_propietario(db: Session, propietario_id) -> list[Vehiculo]:
    """
    Lista los vehículos registrados por un propietario.

    Alcance Sprint 1:
        - permite verificar desde el dashboard que los vehículos publicados
          quedaron registrados.
        - no implementa catálogo público.
        - no implementa filtros, reservas, edición ni eliminación.
    """
    propietario = (
        db.query(Usuario)
        .filter(Usuario.id == propietario_id)
        .first()
    )

    if propietario is None:
        raise UsuarioNoEncontradoError()

    return (
        db.query(Vehiculo)
        .filter(Vehiculo.propietario_id == propietario_id)
        .all()
    )

def cargar_documentacion_vehiculo(
    db: Session,
    vehiculo_id,
    schema: DocumentacionVehiculoSchema,
) -> Vehiculo:
    """
    Carga la documentación legal y operativa de un vehículo existente.

    Carga la documentación legal y operativa de un vehículo existente.

    Este flujo actualiza el estado de la solicitud para que un administrador
    lo revise (US 4D).

    Args:
        db          : Sesión SQLAlchemy activa.
        vehiculo_id : Identificador del vehículo.
        schema      : Payload documental validado por Pydantic.

    Returns:
        Vehiculo actualizado con documentación legal.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    if vehiculo.estado_registro not in ESTADOS_DOCUMENTACION_EDITABLE:
        raise DocumentacionVehiculoNoEditableError()

    vehiculo.patente = schema.patente
    vehiculo.chasis = schema.chasis
    vehiculo.motor = schema.motor
    vehiculo.titular = schema.titular
    vehiculo.cedula = schema.cedula
    vehiculo.poliza = schema.poliza
    vehiculo.vtv = schema.vtv
    vehiculo.estacion = schema.estacion
    vehiculo.telefono = schema.telefono
    vehiculo.descripcion = schema.descripcion
    
    # Cambia a estado EN_REVISION para la US 4D
    vehiculo.estado_registro = "EN_REVISION"
    # Si estaba rechazado, limpiamos el motivo
    vehiculo.motivo_rechazo = None
    cerrar_notificacion_documentacion_pendiente(db=db, vehiculo=vehiculo)

    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def verificar_alquileres_activos(db: Session, vehiculo_id: uuid.UUID) -> bool:
    """
    Verifica si un vehículo tiene reservas o alquileres que bloquean su baja
    de disponibilidad.
    """
    reserva_activa = (
        db.query(Reserva.id)
        .filter(
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.estado.in_(ESTADOS_RESERVA_QUE_BLOQUEAN_DISPONIBILIDAD),
        )
        .first()
    )
    return reserva_activa is not None


def cambiar_disponibilidad_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    disponible: bool,
) -> Vehiculo:
    """
    Cambia el estado de disponibilidad del vehículo para alquiler.

    Args:
        db: Sesión SQLAlchemy.
        vehiculo_id: UUID del vehículo.
        disponible: Nuevo estado de disponibilidad (True/False).

    Returns:
        Vehiculo actualizado.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
        VehiculoNoHabilitadoError: Si el auto no está HABILITADO.
        VehiculoConReservaActivaError: Si se intenta deshabilitar y tiene alquileres.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    if vehiculo.estado_registro != "HABILITADO":
        raise VehiculoNoHabilitadoError()

    if not disponible and verificar_alquileres_activos(db=db, vehiculo_id=vehiculo_id):
        raise VehiculoConReservaActivaError()

    vehiculo.disponible = disponible

    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def listar_vehiculos_disponibles(db: Session) -> list[Vehiculo]:
    """
    Lista todos los vehículos que están habilitados y disponibles para alquiler,
    y que tienen un precio por día definido.
    """
    return (
        db.query(Vehiculo)
        .filter(
            Vehiculo.estado_registro == "HABILITADO",
            Vehiculo.disponible == True,
            Vehiculo.precio_por_dia.isnot(None),
            Vehiculo.precio_por_dia > 0
        )
        .all()
    )
