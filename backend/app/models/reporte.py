"""
Modelo ORM — US 16C: Gestion de incidentes y reportes de siniestros en curso.

Representa el reporte de un incidente ocurrido durante una contratación.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reporte(Base):
    """Reporte de un incidente ocurrido durante una contratación."""

    __tablename__ = "reportes"

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
        doc="Reserva en la que se genero el reporte.",
    )

    conductor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
        doc="Conductor que genero el reporte.",
    )

    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehiculos.id"),
        nullable=False,
        index=True,
        doc="Vehículo en el que ocurrió el incidente.",
    )

    descripcion: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        doc="Texto libre del conductor describiendo el problema.",
    )

    url_foto_adjuntada: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="URL de la foto adjuntada por el conductor (opcional).",
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
            f"<Reporte id={self.id} reserva_id={self.reserva_id} "
        )