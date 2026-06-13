"""
Modelo ORM — US 14C: Obtener código de reserva.

Representa una contratación/reserva confirmada de un vehículo por un conductor.
"""
from decimal import Decimal
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reserva(Base):
    """Reserva confirmada con código único de retiro."""

    __tablename__ = "reservas"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID v4 generado en la capa de aplicación.",
    )

    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehiculos.id"),
        nullable=False,
        index=True,
        doc="Vehículo reservado.",
    )
    conductor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
        doc="Usuario conductor que realiza la reserva.",
    )

    codigo: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        index=True,
        doc="Código único visible que el conductor presenta en la estación.",
    )
    codigo_verificado_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Fecha/hora UTC de la primera verificación del código. Null significa válido.",
    )

    estado: Mapped[str] = mapped_column(
        String(50),
        default="CONFIRMADA",
        nullable=False,
        index=True,
        doc="Estado de la reserva/contratación.",
    )
    monto_total: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
        doc="Monto total calculado para el período reservado.",
    )
    motivo_rechazo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Motivo ingresado por el admin cuando la reserva se rechaza.",
    )

    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Fecha y hora pactada de inicio del alquiler.",
    )
    fecha_fin: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Fecha y hora pactada de finalización del alquiler.",
    )
    estacion_retiro: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Estación pactada originalmente para el retiro.",
    )

    # ── Tiempos reales ──────────────────────────────────────────
    fecha_entrega_solicitada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Momento en que el conductor avisó que entrega el auto (auditoría).",
    )
    fecha_salida_real: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Fecha/hora real en que el auto salió de la estación.",
    )
    fecha_devolucion_real: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Fecha/hora real en que el auto fue devuelto en la estación.",
    )
    minutos_retraso: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Minutos de retraso al avisar la entrega respecto de fecha_fin.",
    )
    monto_penalizacion: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Recargo calculado al avisar entrega tardía.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    vehiculo = relationship("Vehiculo")
    conductor = relationship("Usuario")
    checkin = relationship(
        "CheckinVehiculo",
        back_populates="reserva",
        uselist=False,
        doc="Check-in del conductor asociado a esta reserva (relación 1 a 1).",
    )

    def __repr__(self) -> str:
        return (
            f"<Reserva id={self.id} codigo={self.codigo} "
            f"vehiculo_id={self.vehiculo_id} conductor_id={self.conductor_id}>"
        )
