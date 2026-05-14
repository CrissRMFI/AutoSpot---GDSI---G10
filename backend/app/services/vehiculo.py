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
from sqlalchemy.orm import Session

from app.exceptions import UsuarioNoEncontradoError, VehiculoNoEncontradoError
from app.models.foto_vehiculo import FotoVehiculo
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo import RegistroVehiculoSchema


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
