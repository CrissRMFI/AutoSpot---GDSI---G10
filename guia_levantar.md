# Guía para levantar AutoSpot localmente

## Stack del proyecto

- Backend: Python + FastAPI + SQLAlchemy + Alembic
- Base de datos: PostgreSQL con Docker
- Frontend: React + Vite
- API local: `http://localhost:8000`
- Frontend local: `http://localhost:5173`
- PostgreSQL local: `localhost:5433`

---

## 1. Ubicarse en la carpeta raíz del proyecto

La carpeta raíz es la que contiene:

```txt
autospot/
├── backend/
├── frontend/
├── docker-compose.yml
└── .env
```

Verificar:

```bash
ls
```

Deberían aparecer `backend`, `frontend` y `docker-compose.yml`.

---

## 2. Crear el `.env` de la raíz

En la raíz del proyecto, crear un archivo llamado `.env`.

```txt
autospot/.env
```

Contenido:

```env
DB_USER=autospot_user
DB_PASSWORD=autospot_pass
DB_HOST=localhost
DB_PORT=5433
DB_NAME=autospot_db
DB_NAME_TEST=autospot_test_db
```

Importante: este archivo no debe subirse al repositorio si contiene credenciales reales. Para local usamos estas credenciales de desarrollo. Aunque naide nos va arobar autosport je

---

## 3. Crear el `.env` del frontend

Entrar a la carpeta del frontend:

```bash
cd frontend
```

Crear un archivo `.env`.

```txt
autospot/frontend/.env
```

Contenido:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Volver a la raíz:

```bash
cd ..
```

---

## 4. Levantar PostgreSQL local con Docker

Desde la raíz del proyecto:

```bash
docker compose up db -d
```

Verificar que el contenedor esté corriendo:

```bash
docker ps
```

Debería aparecer algo similar a:

```txt
autospot_db   postgres:16-alpine   Up ... (healthy)   0.0.0.0:5433->5432/tcp
```

Si aparece `healthy`, la base está lista.

---

## 5. Levantar el backend

Entrar a backend desde la raíz:

```bash
cd backend
```

Activar el entorno virtual:

```bash
source venv/bin/activate
```

Cargar variables del `.env` de la raíz:

```bash
set -a
source ../.env
set +a
```

Aplicar migraciones de base de datos:

```bash
alembic upgrade head
```

Levantar FastAPI:

```bash
uvicorn app.main:app --reload
```

El backend queda disponible en:

```txt
http://localhost:8000
```

Documentación Swagger:

```txt
http://localhost:8000/docs
```

Dejar esta terminal abierta.

---

## 6. Levantar el frontend

Abrir otra terminal.

Ir al frontend:

Instalar dependencias si es la primera vez:

```bash
npm install
```

Levantar Vite:

```bash
npm run dev
```

El frontend queda disponible normalmente en:

```txt
http://localhost:5173
```

Entrar desde el navegador a esa URL.

---

## 7. Comandos para verificar backend

Desde la raíz:

```bash
cd backend
source venv/bin/activate
set -a
source ../.env
set +a
pytest
```

---

## 9. Comandos para verificar frontend

Desde la raíz:

```bash
cd frontend
npm run build
```

Resultado esperado:

```txt
✓ built
```

También se puede verificar que no queden llamadas hardcodeadas:

```bash
grep -R "localhost:8000" -n src
grep -R "fetch(" -n src
```

Resultado esperado: no debería imprimir nada.

---

## 10. Migraciones

Las migraciones se aplican con Alembic desde la carpeta `backend`.

Comando:

```bash
cd backend
source venv/bin/activate
set -a
source ../.env
set +a
alembic upgrade head
```

Este comando crea o actualiza las tablas necesarias en PostgreSQL.

No hace falta correr migraciones cada vez que se levanta el backend, pero sí conviene correrlas cuando:

- Se levanta la base por primera vez.
- Se borra el volumen de Docker.
- Alguien agrega una nueva migración.
- El backend falla porque falta una tabla o columna.

---

## 11. Reiniciar base de datos desde cero

Atención: esto borra todos los datos locales.

Desde la raíz:

```bash
docker compose down -v
docker compose up db -d
```

Después volver a aplicar migraciones:

```bash
cd backend
source venv/bin/activate
set -a
source ../.env
set +a
alembic upgrade head
```

Luego levantar backend:

```bash
uvicorn app.main:app --reload
```

---

## 12. Problemas comunes

### Error: `permission denied for schema public`

Solución recomendada en local:

```bash
docker compose down -v
docker compose up db -d
```

Luego:

```bash
cd backend
source venv/bin/activate
set -a
source ../.env
set +a
alembic upgrade head
pytest
```

Si sigue fallando, revisar permisos del usuario de PostgreSQL.

---

### Error: `Falta configurar VITE_API_BASE_URL`

Falta crear el archivo:

```txt
frontend/.env
```

Contenido:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Después reiniciar el frontend:

```bash
npm run dev
```

---

### Error: el frontend no conecta con el backend

Revisar:

1. Que el backend esté corriendo en `http://localhost:8000`.
2. Que `frontend/.env` tenga:

```env
VITE_API_BASE_URL=http://localhost:8000
```

3. Que se haya reiniciado Vite después de modificar `.env`.

---

### Error: la base no conecta

Revisar que PostgreSQL esté levantado:

```bash
docker ps
```

Debe aparecer:

```txt
autospot_db
```

Revisar `.env` de la raíz:

```env
DB_HOST=localhost
DB_PORT=5433
```

---

## 13. Resumen rápido de comandos

Terminal 1: base de datos

```bash
cd autospot
docker compose up db -d
```

Terminal 2: backend

```bash
cd autospot/backend
source venv/bin/activate
set -a
source ../.env
set +a
alembic upgrade head
uvicorn app.main:app --reload
```

Terminal 3: frontend

```bash
cd autospot/frontend
npm install
npm run dev
```

URLs:

```txt
Frontend: http://localhost:5173
Backend:  http://localhost:8000
Swagger:  http://localhost:8000/docs
DB:       localhost:5433
```

---

## 14. Estado esperado del Sprint 1

Deberían estar disponibles estos flujos:

- Registro con email y contraseña.
- Inicio de sesión.
- Cierre de sesión.
- Registro de datos personales.
- Actualización de datos personales.
- Publicación de vehículo con características.
- Carga simulada de fotos.
- Definición de precio diario del vehículo.
