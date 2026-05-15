# ══════════════════════════════════════════════════════════════════════════════
# Dockerfile — Backend AutoSpot
#
# Imagen:
#   - Python 3.12 slim
#
# Responsabilidades:
#   1. Instalar dependencias del sistema necesarias para PostgreSQL.
#   2. Instalar dependencias Python.
#   3. Copiar el código del backend.
#   4. Aplicar migraciones Alembic al arrancar.
#   5. Levantar FastAPI con Uvicorn.
# ══════════════════════════════════════════════════════════════════════════════

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]