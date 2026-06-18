"""
Modelo ORM — Fotos asociadas a un reporte de incidencia critica.

Cada reporte de falla critica admite entre 1 y 10 fotos, cada una con
descripcion obligatoria. La validacion de minimo/maximo vive en la capa de
schema/servicio; el modelo solo persiste la relacion.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReporteFoto(Base):
    """Foto adjunta a un reporte de incidencia critica."""

    __tablename__ = "reporte_fotos"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID v4 generado en la capa de aplicación.",
    )

    reporte_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reportes.id"),
        nullable=False,
        index=True,
        doc="Reporte al que pertenece la foto.",
    )

    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="URL pública de la foto en Cloudinary.",
    )

    descripcion: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Descripción obligatoria de la foto.",
    )

    formato: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Formato del archivo (jpg, png, etc.).",
    )

    tamanio_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Tamaño del archivo en bytes.",
    )

    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Orden de la foto dentro del reporte (>= 1).",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    reporte = relationship("Reporte", back_populates="fotos")

    def __repr__(self) -> str:
        return f"<ReporteFoto id={self.id} reporte_id={self.reporte_id} orden={self.orden}>"
