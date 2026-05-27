"""
Modelo ORM — Notificaciones de usuario.

Representa avisos persistentes para cerrar el ciclo de feedback de una US.
Por ahora se usa para informar al propietario cuando un vehículo fue
habilitado o rechazado por administración.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Notificacion(Base):
    """
    Notificación dirigida a un usuario autenticado.

    `vista_at` en NULL significa que todavía debe mostrarse en la campana.
    Cuando el usuario la abre, se guarda la fecha y deja de aparecer en el
    listado de notificaciones nuevas.
    """

    __tablename__ = "notificaciones"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID v4 generado en la capa de aplicación.",
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
        doc="Usuario destinatario de la notificación.",
    )
    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Tipo funcional de notificación.",
    )
    titulo: Mapped[str] = mapped_column(
        String(140),
        nullable=False,
        doc="Título breve visible en la UI.",
    )
    mensaje: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Detalle visible de la notificación.",
    )
    recurso_tipo: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Tipo de recurso asociado, por ejemplo VEHICULO.",
    )
    recurso_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True,
        doc="UUID del recurso asociado.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp UTC de creación.",
    )
    vista_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp UTC de lectura/vista. NULL = pendiente de mostrar.",
    )

    def __repr__(self) -> str:
        return (
            f"<Notificacion id={self.id} usuario_id={self.usuario_id} "
            f"tipo={self.tipo}>"
        )
