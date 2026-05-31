"""
Modelo ORM — US 15C: Check-in de Vehículo.

Representa el registro del estado inicial del vehículo por parte del conductor.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CheckinVehiculo(Base):
    """
    Registro del estado inicial del vehículo.
    """

    __tablename__ = "checkins_vehiculo"

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
        doc="Reserva a la que pertenece este check-in (1 a 1).",
    )
    conductor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
        doc="Usuario conductor que realiza el check-in.",
    )

    nivel_combustible: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Nivel de combustible: 1/4, 1/2, 3/4, Lleno.",
    )
    kilometraje_actual: Mapped[int] = mapped_column(
        nullable=False,
        doc="Kilometraje marcado en el panel al momento del retiro.",
    )
    esta_limpio: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Indicador de si el vehículo está limpio.",
    )
    tiene_danios: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Indicador de si el vehículo presenta rayas o daños.",
    )
    descripcion_danios: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Descripción del daño si tiene_danios es True.",
    )

    # Fotos obligatorias
    url_foto_frente: Mapped[str] = mapped_column(String(255), nullable=False)
    url_foto_trasera: Mapped[str] = mapped_column(String(255), nullable=False)
    url_foto_lateral_izq: Mapped[str] = mapped_column(String(255), nullable=False)
    url_foto_lateral_der: Mapped[str] = mapped_column(String(255), nullable=False)
    url_foto_panel: Mapped[str] = mapped_column(String(255), nullable=False)

    # Fotos opcionales
    urls_fotos_danios: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="Lista de URLs de fotos de daños (máximo 5).",
    )
    url_foto_extra: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notas_adicionales: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    # Estado de revisión
    estado: Mapped[str] = mapped_column(
        String(20),
        default="PENDIENTE",
        nullable=False,
        index=True,
        doc="PENDIENTE, APROBADO o RECHAZADO.",
    )
    motivo_rechazo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Motivo detallado si el check-in es rechazado.",
    )

    # Auditoría
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

    reserva = relationship("Reserva")
    conductor = relationship("Usuario")

    def __repr__(self) -> str:
        return (
            f"<CheckinVehiculo id={self.id} reserva_id={self.reserva_id} "
            f"estado={self.estado}>"
        )
