"""
Modelo ORM: TokenBlacklist (US 3U — Invalidación de sesiones).

Arquitectura:
  - Tabla `tokens_blacklist` almacena los `jti` (JWT ID) de tokens invalidados
    por logout manual (CA1).
  - Cada registro tiene un `expires_at` para poder purgar tokens expirados
    periódicamente (los tokens expirados ya no necesitan estar en la blacklist
    porque PyJWT los rechaza automáticamente por `exp`).

Flujo:
  1. POST /usuarios/logout → se extrae `jti` del token → se inserta aquí.
  2. En cada request autenticado → se verifica que `jti` NO esté en esta tabla.
  3. Si `jti` está en la blacklist → 401 Unauthorized (sesión ya finalizada).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TokenBlacklist(Base):
    """
    Registro de tokens JWT invalidados por logout.

    El `jti` (JWT ID) es el identificador único de cada token emitido.
    Al hacer logout, el `jti` se persiste aquí para impedir su reutilización.
    """

    __tablename__ = "tokens_blacklist"

    # ── Identificador ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID interno del registro de blacklist.",
    )

    # ── JTI del token invalidado ─────────────────────────────────────────────
    jti: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
        doc="JWT ID (claim `jti`) del token invalidado.",
    )

    # ── Expiración original del token ────────────────────────────────────────
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc=(
            "Timestamp de expiración original del token. "
            "Permite purgar registros de tokens que ya expiraron naturalmente."
        ),
    )

    # ── Auditoría ────────────────────────────────────────────────────────────
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp UTC de cuándo se invalidó el token (momento del logout).",
    )

    def __repr__(self) -> str:
        return f"<TokenBlacklist jti={self.jti}>"
