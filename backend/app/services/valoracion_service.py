"""
Servicio de dominio — US 17C: Valoración cuantitativa del servicio.

Responsabilidades:
    1. Validar que la reserva esté FINALIZADA con devolución física.
    2. Impedir valoraciones duplicadas.
    3. Persistir la valoración.
    4. Recalcular el promedio del vehículo (media de puntajes recibidos).
    5. Recalcular el promedio del propietario (media de los promedios
       de todos sus vehículos que tengan calificación).
"""
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.exceptions import (
    ReservaNoEncontradaError,
    ReservaNoFinalizadaError,
    ValoracionYaRegistradaError,
)
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.valoracion import Valoracion
from app.models.vehiculo import Vehiculo


def crear_valoracion(
    db: Session,
    reserva_id: str,
    conductor_id: str,
    puntaje: int,
) -> Valoracion:
    """
    Registra una valoración y recalcula promedios.

    Args:
        db: Sesión activa de SQLAlchemy.
        reserva_id: UUID de la reserva a valorar.
        conductor_id: UUID del conductor que emite la valoración.
        puntaje: Entero de 1 a 5 (ya validado por Pydantic).

    Returns:
        La entidad Valoracion recién creada.

    Raises:
        ReservaNoEncontradaError: si la reserva no existe.
        ReservaNoFinalizadaError: si la reserva no está FINALIZADA
            o no tiene devolución registrada.
        ValoracionYaRegistradaError: si ya existe una valoración para
            esa reserva.
    """
    # 1. Buscar la reserva
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if reserva is None:
        raise ReservaNoEncontradaError()

    # 2. Validar estado FINALIZADA con devolución física
    if reserva.estado != "FINALIZADA" or reserva.fecha_devolucion_real is None:
        raise ReservaNoFinalizadaError()

    # 3. Validar que no exista valoración previa
    existente = (
        db.query(Valoracion)
        .filter(Valoracion.reserva_id == reserva_id)
        .first()
    )
    if existente is not None:
        raise ValoracionYaRegistradaError()

    # 4. Crear y persistir la valoración
    valoracion = Valoracion(
        reserva_id=reserva_id,
        conductor_id=conductor_id,
        vehiculo_id=reserva.vehiculo_id,
        puntaje=puntaje,
    )
    db.add(valoracion)
    db.flush()  # Asegurar que la valoración está en la sesión para el cálculo

    # 5. Recalcular promedio del vehículo
    _recalcular_promedio_vehiculo(db, reserva.vehiculo_id)
    db.flush()  # Persistir promedio del vehículo antes de calcular el del propietario

    # 6. Recalcular promedio del propietario
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == reserva.vehiculo_id).first()
    _recalcular_promedio_propietario(db, vehiculo.propietario_id)

    db.commit()
    db.refresh(valoracion)

    return valoracion


def _recalcular_promedio_vehiculo(db: Session, vehiculo_id) -> None:
    """
    Calcula la media aritmética de todos los puntajes de valoraciones
    recibidas por el vehículo y actualiza su campo calificacion_promedio.
    """
    promedio = (
        db.query(func.avg(Valoracion.puntaje))
        .filter(Valoracion.vehiculo_id == vehiculo_id)
        .scalar()
    )

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if vehiculo is not None:
        vehiculo.calificacion_promedio = (
            Decimal(str(round(float(promedio), 2))) if promedio else None
        )


def _recalcular_promedio_propietario(db: Session, propietario_id) -> None:
    """
    Calcula la media de los promedios de calificación de TODOS los vehículos
    del propietario que tienen calificación, y actualiza el campo
    calificacion_promedio del usuario propietario.

    Regla de negocio:
        promedio_propietario = AVG(vehiculo.calificacion_promedio)
        para todos los vehículos del propietario con calificación != NULL.
    """
    promedio = (
        db.query(func.avg(Vehiculo.calificacion_promedio))
        .filter(
            Vehiculo.propietario_id == propietario_id,
            Vehiculo.calificacion_promedio.isnot(None),
        )
        .scalar()
    )

    propietario = db.query(Usuario).filter(Usuario.id == propietario_id).first()
    if propietario is not None:
        propietario.calificacion_promedio = (
            Decimal(str(round(float(promedio), 2))) if promedio else None
        )
