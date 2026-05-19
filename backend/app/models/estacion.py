from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Estacion(Base):
    """
    Modelo ORM para Estación (US 4C).
    Representa una ubicación física de AutoSpot para el retiro y entrega de Activos.
    """

    __tablename__ = "estaciones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    instrucciones_acceso: Mapped[str] = mapped_column(String(1000), nullable=False)
    zona: Mapped[str] = mapped_column(String(100), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Estacion id={self.id} nombre='{self.nombre}' activa={self.activa}>"
