"""
Modelo ORM — US 1U: Datos personales del Usuario.

Esta entidad representa la documentación personal cargada por un Usuario
que ya posee una cuenta creada en la plataforma.

Criterios de Aceptación cubiertos por la entidad:
    CA1 → DNI, nombre y apellido registrados.
    CA2 → foto frente y dorso del DNI registradas.

Regla de diseño:
    Un Usuario puede tener cero o un registro de datos personales.
    Por eso `usuario_id` es único.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DatosPersonalesUsuario(Base):
    """
    Datos personales y documentación básica asociada a un Usuario.

    La validación documental propiamente dicha será responsabilidad de
    historias futuras vinculadas a revisión/auditoría.
    """

    __tablename__ = "datos_personales_usuario"

    __table_args__ = (
        UniqueConstraint("usuario_id", name="uq_datos_personales_usuario_id"),
        UniqueConstraint("dni", name="uq_datos_personales_dni"),
    )

    # ── Identificador ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID v4 generado en la capa de aplicación.",
    )

    # ── Relación con Usuario ─────────────────────────────────────────────────
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
        doc="Usuario al que pertenecen estos datos personales.",
    )

    # ── Datos personales (CA1) ───────────────────────────────────────────────
    dni: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Documento Nacional de Identidad del Usuario.",
    )
    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Nombre del Usuario.",
    )
    apellido: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Apellido del Usuario.",
    )

    # ── Documentación DNI (CA2) ──────────────────────────────────────────────
    foto_dni_frente_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Ruta o URL de la foto del frente del DNI.",
    )
    foto_dni_dorso_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Ruta o URL de la foto del dorso del DNI.",
    )

    # ── Estado documental ────────────────────────────────────────────────────
    estado_validacion: Mapped[str] = mapped_column(
        String(50),
        default="PENDIENTE_VALIDACION",
        nullable=False,
        doc="Estado inicial de validación documental.",
    )

    # ── Auditoría ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp UTC de creación del registro.",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp UTC de última actualización del registro.",
    )

    def __repr__(self) -> str:
        return (
            f"<DatosPersonalesUsuario id={self.id} "
            f"usuario_id={self.usuario_id} dni={self.dni}>"
        )
