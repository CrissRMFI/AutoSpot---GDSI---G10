"""
Modelo ORM — US 1C: Documentación habilitante del Conductor.

Esta entidad representa la documentación que habilita a un Usuario en su rol
de Conductor a contratar Activos en AutoSpot (Licencia de Conducir).

Criterios de Aceptación cubiertos por la entidad:
    CA1 → número de licencia, categoría y fechas de emisión/vencimiento.
    CA2 → foto frente y dorso de la licencia.
    CA5 → permite actualización conservando la asociación con el Usuario.

Regla de diseño:
    Un Usuario puede tener cero o un registro de documentación habilitante.
    Por eso `usuario_id` es único.
"""
import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EstadoHabilitacion(str, enum.Enum):
    """Estados posibles de la habilitación del conductor (US 2C)."""

    PENDIENTE_REVISION = "PENDIENTE_REVISION"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


class DocumentacionHabilitanteConductor(Base):
    """
    Documentación habilitante (Licencia de Conducir) asociada a un Usuario
    en su rol de Conductor.

    La validación documental queda a cargo del Operador de Estación en
    historias futuras (KYC). Aquí solo se registra y se persiste el estado
    inicial PENDIENTE_VALIDACION.
    """

    __tablename__ = "documentacion_habilitante_conductor"

    __table_args__ = (
        UniqueConstraint(
            "usuario_id",
            name="uq_documentacion_habilitante_conductor_usuario_id",
        ),
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
        doc="Usuario al que pertenece la documentación habilitante.",
    )

    # ── Datos de la licencia (CA1) ───────────────────────────────────────────
    categoria: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        doc="Categoría/clase de la licencia para autos (B1, B2).",
    )
    fecha_emision: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Fecha de emisión de la licencia.",
    )
    fecha_vencimiento: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Fecha de vencimiento de la licencia.",
    )

    # ── Documentación adjunta (CA2) ──────────────────────────────────────────
    foto_licencia_frente_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Ruta o URL de la foto del frente de la licencia.",
    )
    foto_licencia_dorso_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Ruta o URL de la foto del dorso de la licencia.",
    )

    # ── Estado documental (US 2C) ─────────────────────────────────────────────
    estado_validacion: Mapped[str] = mapped_column(
        Enum(EstadoHabilitacion, name="estado_habilitacion_enum", native_enum=True),
        default=EstadoHabilitacion.PENDIENTE_REVISION,
        nullable=False,
        doc="Estado de la habilitación: PENDIENTE_REVISION, APROBADO o RECHAZADO.",
    )

    motivo_rechazo: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        doc="Motivo del rechazo (completado por el administrador). Null si no fue rechazado.",
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
            f"<DocumentacionHabilitanteConductor id={self.id} "
            f"usuario_id={self.usuario_id} categoria={self.categoria}>"
        )
