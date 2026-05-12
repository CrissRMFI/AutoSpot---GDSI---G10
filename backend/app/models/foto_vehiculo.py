"""
Modelo ORM — US 1D: Foto de vehículo.

Representa una foto asociada a un vehículo registrado. Por ahora se guardan
metadatos y una URL/ruta, no el archivo binario.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FotoVehiculo(Base):
    """
    Foto asociada a un vehículo.

    Lados esperados:
        FRENTE
        TRASERA
        LATERAL_IZQUIERDO
        LATERAL_DERECHO
    """

    __tablename__ = "fotos_vehiculo"

    # ── Identificador ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID v4 generado en la capa de aplicación.",
    )

    # ── Relación con Vehículo ────────────────────────────────────────────────
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehiculos.id"),
        nullable=False,
        index=True,
        doc="Vehículo al que pertenece la foto.",
    )

    vehiculo: Mapped["Vehiculo"] = relationship(
        "Vehiculo",
        back_populates="fotos",
    )

    # ── Datos de foto ────────────────────────────────────────────────────────
    lado: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Lado del vehículo fotografiado.",
    )
    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Ruta o URL de la foto.",
    )
    formato: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Formato del archivo: jpg, jpeg, png o webp.",
    )
    tamanio_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Tamaño del archivo en bytes.",
    )

    # ── Auditoría ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp UTC de creación del registro.",
    )

    def __repr__(self) -> str:
        return (
            f"<FotoVehiculo id={self.id} vehiculo_id={self.vehiculo_id} "
            f"lado={self.lado}>"
        )
