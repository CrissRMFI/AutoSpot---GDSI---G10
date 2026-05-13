"""
Modelo ORM — US 1D: Vehículo.

Representa el activo que un dueño registra en la plataforma con sus
características obligatorias. Las fotos se modelan en una entidad separada
para permitir múltiples imágenes asociadas al mismo vehículo.
"""
from decimal import Decimal
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vehiculo(Base):
    """
    Vehículo registrado por un usuario propietario.
    
    En esta etapa se usa `propietario_id` apuntando a `usuarios.id`
    porque todavía no existe una especialización formal de Propietario.
    """

    __tablename__ = "vehiculos"

    # ── Identificador ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID v4 generado en la capa de aplicación.",
    )

    # ── Relación temporal con Usuario propietario ────────────────────────────
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
        doc="Usuario dueño del vehículo. Temporal hasta modelar Propietario.",
    )

    # ── Características obligatorias (US 1D) ─────────────────────────────────
    marca: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Marca del vehículo.",
    )
    modelo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Modelo del vehículo.",
    )
    anio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Año del vehículo.",
    )
    tipo_transmision: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Tipo de transmisión del vehículo.",
    )
    capacidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Cantidad de pasajeros/asientos.",
    )
    categoria: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Categoría del vehículo.",
    )
    tipo_combustible: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Tipo de combustible.",
    )
    pets_friendly: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        doc="Indica si el vehículo acepta mascotas.",
    )
    # ── Datos legales y de documentación ─────────────────────────────────────
    patente: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        doc="Patente del vehículo.",
    )
    chasis: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Número de chasis.",
    )
    motor: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Número de motor.",
    )
    titular: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Titular registral del vehículo.",
    )
    cedula: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Cédula verde (número o estado).",
    )
    poliza: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Número de póliza de seguro.",
    )
    vtv: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="VTV (fecha de vencimiento o constancia).",
    )
    estacion: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Estación asignada.",
    )
    telefono: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Teléfono de contacto.",
    )
    descripcion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Descripción legal y operativa del vehículo.",
    )
    # ── Tarifa diaria (US 5D) ────────────────────────────────────────────────
    precio_por_dia: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=True,
        doc="Tarifa diaria definida por el propietario para alquilar el vehículo.",
    )

    # ── Estado del registro ──────────────────────────────────────────────────
    estado_registro: Mapped[str] = mapped_column(
        String(50),
        default="PENDIENTE_DOCUMENTACION",
        nullable=False,
        doc="Estado inicial tras cargar características y fotos.",
    )

    # ── Relación con fotos ───────────────────────────────────────────────────
    fotos: Mapped[list["FotoVehiculo"]] = relationship(
        "FotoVehiculo",
        back_populates="vehiculo",
        cascade="all, delete-orphan",
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
        doc="Timestamp UTC de última actualización.",
    )

    def __repr__(self) -> str:
        return (
            f"<Vehiculo id={self.id} marca={self.marca} "
            f"modelo={self.modelo} propietario_id={self.propietario_id}>"
        )
