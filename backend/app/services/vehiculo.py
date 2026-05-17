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
    UsuarioNoEncontradoError,
    VehiculoNoEncontradoError,
    VehiculoNoHabilitadoError,
    VehiculoConReservaActivaError,
)
from app.models.foto_vehiculo import FotoVehiculo
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo import (
    DocumentacionVehiculoSchema,
    RegistroVehiculoSchema,
)

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
    """
    propietario = (
        db.query(Usuario)
        .filter(Usuario.id == schema.propietario_id)
        .first()
    )
    if propietario is None:
        raise UsuarioNoEncontradoError()

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

    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def verificar_alquileres_activos(vehiculo_id: uuid.UUID) -> bool:
    """
    Stub temporal para verificar si un vehículo tiene alquileres o reservas
    en curso. En un futuro, delegará al servicio correspondiente de alquileres.
    """
    # TODO: Implementar lógica real cuando exista el módulo de alquileres
    return False


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

    if not disponible and verificar_alquileres_activos(vehiculo_id):
        raise VehiculoConReservaActivaError()

    vehiculo.disponible = disponible

    db.commit()
    db.refresh(vehiculo)

    return vehiculo