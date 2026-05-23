"""
Modelos ORM — Catálogo de marcas y modelos de vehículos.

Reemplaza el catálogo hardcodeado que vivía en `app/schemas/vehiculo.py`.
La administración del catálogo se hace por endpoints HTTP (Postman/Insomnia)
y se consume desde el frontend en GET /marcas.

Decisión de diseño:
    `vehiculos.marca` y `vehiculos.modelo` permanecen como strings (sin FK)
    para no requerir migración de datos existentes. La validación de que la
    combinación marca/modelo exista en el catálogo se hace en la capa de
    servicio al crear/actualizar un vehículo.
"""
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Marca(Base):
    """Marca de vehículo (ej. Toyota, Ford)."""

    __tablename__ = "marcas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    modelos: Mapped[list["Modelo"]] = relationship(
        "Modelo",
        back_populates="marca",
        cascade="all, delete-orphan",
        order_by="Modelo.nombre",
    )

    def __repr__(self) -> str:
        return f"<Marca id={self.id} nombre='{self.nombre}'>"


class Modelo(Base):
    """Modelo de vehículo asociado a una marca (ej. Corolla → Toyota)."""

    __tablename__ = "modelos"
    __table_args__ = (
        UniqueConstraint("marca_id", "nombre", name="uq_modelos_marca_nombre"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    marca_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("marcas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    marca: Mapped["Marca"] = relationship("Marca", back_populates="modelos")

    def __repr__(self) -> str:
        return f"<Modelo id={self.id} nombre='{self.nombre}' marca_id={self.marca_id}>"
