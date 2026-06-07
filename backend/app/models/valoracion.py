"""
Modelo ORM — US 17C: Valoración cuantitativa del servicio.

Representa el puntaje numérico (1–5) que un conductor asigna a una
contratación finalizada con devolución física registrada.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Valoracion(Base):
    """Valoración cuantitativa de un servicio de alquiler."""

    __tablename__ = "valoraciones"

    __table_args__ = (
        UniqueConstraint("reserva_id", name="uq_valoraciones_reserva_id"),
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
        doc="Reserva finalizada que se está valorando (1 a 1).",
    )
    conductor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
        doc="Conductor que emite la valoración.",
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehiculos.id"),
        nullable=False,
        index=True,
        doc="Vehículo valorado (desnormalizado para facilitar cálculo de promedios).",
    )

    puntaje: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Puntaje numérico del 1 al 5.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    reserva = relationship("Reserva")
    conductor = relationship("Usuario")
    vehiculo = relationship("Vehiculo")

    def __repr__(self) -> str:
        return (
            f"<Valoracion id={self.id} reserva_id={self.reserva_id} "
            f"puntaje={self.puntaje}>"
        )
