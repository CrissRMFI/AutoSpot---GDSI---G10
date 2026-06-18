"""
Modelo ORM — US 16C: Gestion de incidentes y reportes de siniestros en curso.

Representa el reporte de un incidente ocurrido durante una contratación.
A partir de la US de reportes criticos el reporte incorpora tipo, criticidad,
estado, datos de resolucion y una coleccion de fotos (1 a 10).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

TIPO_FALLA = "FALLA"
CRITICIDAD_CRITICA = "CRITICA"
ESTADO_ACTIVO = "ACTIVO"
ESTADO_RESUELTO = "RESUELTO"


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

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=TIPO_FALLA,
        server_default=TIPO_FALLA,
        doc="Tipo de reporte. Por ahora siempre FALLA.",
    )

    criticidad: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=CRITICIDAD_CRITICA,
        server_default=CRITICIDAD_CRITICA,
        doc="Criticidad del reporte. Por ahora siempre CRITICA.",
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=ESTADO_ACTIVO,
        server_default=ESTADO_ACTIVO,
        index=True,
        doc="Estado del reporte: ACTIVO o RESUELTO.",
    )

    resuelto_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Fecha/hora UTC en que se resolvió el reporte.",
    )

    resuelto_por_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=True,
        doc="Usuario (admin o propietario) que resolvió el reporte.",
    )

    resolucion_descripcion: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        doc="Descripción de la resolución registrada.",
    )

    url_foto_adjuntada: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Columna legacy: una sola URL de foto. No se usa en el nuevo flujo.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    reserva = relationship("Reserva")
    conductor = relationship("Usuario", foreign_keys=[conductor_id])
    resuelto_por = relationship("Usuario", foreign_keys=[resuelto_por_id])
    vehiculo = relationship("Vehiculo")
    fotos = relationship(
        "ReporteFoto",
        back_populates="reporte",
        order_by="ReporteFoto.orden",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Reporte id={self.id} reserva_id={self.reserva_id} estado={self.estado}>"
        )
