"""
Checkout de Vehículo.

Representa el registro del estado del vehículo al momento de la devolución,
inspeccionado por el recepcionista. Es el espejo del check-in pero
sobre la entrega/recepción del activo.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CheckoutVehiculo(Base):
    """
    Registro del estado del vehículo en la devolución.
    """

    __tablename__ = "checkouts_vehiculo"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID v4 generado en la capa de aplicación.",
    )

    reserva_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reservas.id"),
        nullable=False,
        index=True,
        doc="Reserva a la que pertenece este checkout (1 a N: historial de intentos).",
    )
    recepcionista_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
        doc="Usuario recepcionista (ADMIN) que realiza la inspección de devolución.",
    )

    nivel_combustible: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Nivel de combustible: 1/4, 1/2, 3/4, Lleno.",
    )
    kilometraje_actual: Mapped[int] = mapped_column(
        nullable=False,
        doc="Kilometraje marcado en el panel al momento de la devolución.",
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

    # Estado de confirmación por el conductor
    estado: Mapped[str] = mapped_column(
        String(30),
        default="PENDIENTE_CONFIRMACION",
        nullable=False,
        index=True,
        doc="PENDIENTE_CONFIRMACION, CONFIRMADO o RECHAZADO.",
    )
    motivo_rechazo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Motivo si el conductor rechaza el checkout.",
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
    recepcionista = relationship("Usuario")

    def __repr__(self) -> str:
        return (
            f"<CheckoutVehiculo id={self.id} reserva_id={self.reserva_id}>"
        )
