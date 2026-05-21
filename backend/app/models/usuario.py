"""
Modelo ORM: Usuario (entidad base).

Arquitectura: Tabla por Rol (Table-Per-Hierarchy con tablas separadas)
  - `usuarios`    ← esta tabla (datos comunes de autenticación)
  - `conductores` ← especialización del Actor Conductor  (US futura)
  - `propietarios`← especialización del Actor Propietario (US futura)

Lenguaje Ubicuo (dominio_actores.md):
  - El término "auto" se reemplaza por "Activo / Vehículo".
  - El término "reserva/alquiler" se reemplaza por "Contratación / Operación".
  - Este modelo corresponde a la capa de AUTENTICACIÓN, previa a la especialización
    por rol (Conductor o Propietario).

US 5U - Criterio de unicidad:
  - `email` tiene restricción UNIQUE a nivel de base de datos (UniqueConstraint).
  - El índice compuesto garantiza performance en búsquedas por email.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Usuario(Base):
    """
    Entidad base de autenticación del sistema AutoSpot.

    Todos los actores del sistema (Conductor, Propietario, Operador de Estación)
    son instancias de Usuario con un rol asociado en su tabla de especialización.
    En la US 5U sólo se persisten email y contraseña hasheada; los datos
    personales se completan en la US 1U.
    """

    __tablename__ = "usuarios"

    __table_args__ = (
        # Restricción de unicidad a nivel DB (redundante con unique=True
        # del campo, pero documentada explícitamente para Alembic).
        UniqueConstraint("email", name="uq_usuarios_email"),
    )

    # ── Identificador ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID v4 generado en la capa de aplicación.",
    )

    # ── Credenciales (US 5U) ─────────────────────────────────────────────────
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Correo electrónico único. Normalizado a minúsculas antes de persistir.",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hash bcrypt de la contraseña. NUNCA se almacena texto plano.",
    )

    # ── Estado de la cuenta ──────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="False = cuenta suspendida o pendiente de verificación.",
    )

    # ── Rol del usuario ──────────────────────────────────────────────────────
    rol: Mapped[str] = mapped_column(
        String(20),
        default="CLIENTE",
        server_default="CLIENTE",
        nullable=False,
        doc="Rol del usuario: CLIENTE, PROPIETARIO o ADMIN. ADMIN solo se setea por backoffice.",
    )

    # ── Auditoría ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp UTC de creación del registro.",
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email}>"
