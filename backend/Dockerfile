# ══════════════════════════════════════════════════════════════════════════════
# Dockerfile — AutoSpot Backend (FastAPI + Uvicorn)
#
# Build optimizado:
#   1. Copia requirements.txt primero → cache de dependencias en layer separado.
#   2. Copia el código fuente después → rebuild rápido al cambiar código.
#
# Imagen base: python:3.12-slim (Debian minimal, ~150MB).
# ══════════════════════════════════════════════════════════════════════════════

FROM python:3.12-slim

# Evitar prompts interactivos y archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Dependencias del sistema para psycopg2-binary ────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# ── Dependencias Python (layer cacheado) ─────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Código fuente ────────────────────────────────────────────────────────────
COPY . .

# ── Puerto y comando ────────────────────────────────────────────────────────
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
