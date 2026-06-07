"""
Servicio — US 18C: Testimonio descriptivo de la experiencia.

Contiene la lógica de negocio para:
  - Registrar un testimonio vinculado a una reserva finalizada (CA 1).
  - Consultar el histórico público de testimonios de un vehículo (CA 2).
  - Garantizar la inmutabilidad mediante unicidad por reserva (CA 3).
"""
import uuid
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import (
    ReservaNoEncontradaError,
    ReservaNoFinalizadaParaTestimonioError,
    TestimonioYaRegistradoError,
)
from app.models.reserva import Reserva
from app.models.testimonio import Testimonio


def crear_testimonio(
    db: Session,
    reserva_id: uuid.UUID,
    conductor_id: uuid.UUID,
    descripcion: Optional[str],
) -> Testimonio:
    """
    Registra un testimonio descriptivo sobre una reserva finalizada.

    Reglas de negocio (CA 1 y CA 3):
      1. La reserva debe existir → ReservaNoEncontradaError (→ HTTP 404).
      2. La reserva debe estar en estado FINALIZADA → ReservaNoFinalizadaParaTestimonioError (→ HTTP 400).
      3. No debe existir un testimonio previo para esa reserva → TestimonioYaRegistradoError (→ HTTP 409).
      4. La descripción es opcional (puede ser None).

    El vehiculo_id se extrae de la reserva para desnormalizar la vinculación
    permanente al identificador del viaje y del vehículo (CA 1).

    Args:
        db: Sesión activa de SQLAlchemy.
        reserva_id: UUID de la reserva sobre la cual se deja el testimonio.
        conductor_id: UUID del conductor autenticado que emite el testimonio.
        descripcion: Texto libre opcional (máx. 1000 chars validado por Pydantic).

    Returns:
        El objeto Testimonio recién persistido.

    Raises:
        ReservaNoEncontradaError: Si la reserva no existe.
        ReservaNoFinalizadaParaTestimonioError: Si la reserva no está FINALIZADA.
        TestimonioYaRegistradoError: Si ya existe un testimonio para esa reserva.
    """
    # ── 1. Verificar que la reserva existe ────────────────────────────────────
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if reserva is None:
        raise ReservaNoEncontradaError()

    # ── 2. Verificar que la contratación está cerrada administrativamente ──────
    if reserva.estado != "FINALIZADA":
        raise ReservaNoFinalizadaParaTestimonioError()

    # ── 3. Verificar que no existe ya un testimonio para esta reserva ─────────
    existe = (
        db.query(Testimonio)
        .filter(Testimonio.reserva_id == reserva_id)
        .first()
    )
    if existe:
        raise TestimonioYaRegistradoError()

    # ── 4. Crear y persistir el testimonio ────────────────────────────────────
    testimonio = Testimonio(
        id=uuid.uuid4(),
        reserva_id=reserva_id,
        conductor_id=conductor_id,
        vehiculo_id=reserva.vehiculo_id,  # vinculación permanente al vehículo (CA 1)
        descripcion=descripcion,
    )
    db.add(testimonio)

    try:
        db.commit()
    except IntegrityError:
        # Race condition: otro request creó el testimonio entre el check y el commit
        db.rollback()
        raise TestimonioYaRegistradoError()

    db.refresh(testimonio)
    return testimonio


def obtener_testimonios_por_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
) -> list[Testimonio]:
    """
    Devuelve el listado público de testimonios de un vehículo ordenados
    cronológicamente (más reciente primero).

    Es un endpoint público: no requiere autenticación (CA 2).

    Args:
        db: Sesión activa de SQLAlchemy.
        vehiculo_id: UUID del vehículo cuyo histórico se consulta.

    Returns:
        Lista (posiblemente vacía) de objetos Testimonio.
    """
    return (
        db.query(Testimonio)
        .filter(Testimonio.vehiculo_id == vehiculo_id)
        .order_by(Testimonio.created_at.desc())
        .all()
    )
