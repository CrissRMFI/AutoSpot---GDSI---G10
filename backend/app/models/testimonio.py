"""
Modelo ORM — US 18C: Testimonio descriptivo de la experiencia.

Representa el relato cualitativo que un conductor registra sobre una
contratación finalizada. El testimonio es inmutable: no existe endpoint
de actualización ni eliminación.

Restricción de integridad:
  - UniqueConstraint en reserva_id garantiza que solo puede existir un
    testimonio por reserva (CA 3 — inmutabilidad y transparencia).
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Testimonio(Base):
    """Testimonio descriptivo de un servicio de alquiler finalizado."""

    __tablename__ = "testimonios"

    __table_args__ = (
        UniqueConstraint("reserva_id", name="uq_testimonios_reserva_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID v4 generado en la capa de aplicación.",
    )

    reserva_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reservas.id"),
        nullable=False,
        unique=True,
        index=True,
        doc="Reserva finalizada sobre la cual se deja el testimonio (1 a 1).",
    )
    conductor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
        doc="Conductor que emite el testimonio.",
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehiculos.id"),
        nullable=False,
        index=True,
        doc="Vehículo al que corresponde el testimonio (desnormalizado para facilitar consultas).",
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Texto libre del conductor describiendo su experiencia (opcional, máx. 1000 chars).",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────────
    reserva = relationship("Reserva")
    conductor = relationship("Usuario")
    vehiculo = relationship("Vehiculo")

    def __repr__(self) -> str:
        return (
            f"<Testimonio id={self.id} reserva_id={self.reserva_id} "
            f"conductor_id={self.conductor_id}>"
        )
