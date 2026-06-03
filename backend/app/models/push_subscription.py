"""
Modelo ORM — Suscripciones Web Push por usuario.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PushSubscription(Base):
    """
    Suscripcion Push API asociada a un dispositivo/navegador del usuario.

    Un usuario puede tener varias suscripciones activas: celular, notebook,
    escritorio, etc. El endpoint del navegador es unico y se actualiza si el
    mismo dispositivo vuelve a registrarse.
    """

    __tablename__ = "push_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )
    endpoint: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        unique=True,
        index=True,
    )
    p256dh: Mapped[str] = mapped_column(String(255), nullable=False)
    auth: Mapped[str] = mapped_column(String(255), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
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

    def __repr__(self) -> str:
        return f"<PushSubscription id={self.id} usuario_id={self.usuario_id}>"
