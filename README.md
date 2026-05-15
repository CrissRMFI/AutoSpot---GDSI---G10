# AutoSpot

AutoSpot es una aplicación web para la publicación y gestión de vehículos en alquiler.

El proyecto está compuesto por:

- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Base de datos:** PostgreSQL
- **Frontend:** React + Vite
- **Ejecución local containerizada:** Docker Compose

---

## 1. Requisitos previos

Para levantar el proyecto completo con Docker:

- Docker
- Docker Compose

Para trabajar localmente sin Docker:

- Python 3.12+
- Node.js 22+
- npm
- PostgreSQL 16+

---

## 2. Estructura general

```txt
autospot/
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker/
│   └── init-test-db.sql
├── docker-compose.yml
├── .env.example
└── README.md
```

## 3. Variables de entorno

Crear el archivo .env en la raiz del proyecto

```txt
cp .env.example .env
```

Ejemplo de configuración

```txt
DATABASE_URL=
DB_USER=autospot_user
DB_PASSWORD=autospot_pass
DB_HOST=localhost
DB_PORT=5433
DB_NAME=autospot_db
DB_NAME_TEST=autospot_test_db

JWT_SECRET_KEY=generar-una-clave-segura-con-python-secrets-token-urlsafe
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
ENVIRONMENT=development
```

Para generar la clave segura:

```txt
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(64))
PY
```

## 4. Ejecución local con Docker

```txt
docker compose up --build -d
```

Esto levanta
| Servicio | URL / Puerto |
|------------|-----------------------|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| PostgreSQL | localhost:5433 |

Verificar contenedores

```txt
 docker compose ps
```

Verificar Backend

```txt
curl -I http://localhost:8000/docs
```

Verificar Frontend

```txt
curl -I http://localhost:3000
```

## 5. Detener proyecto

Detener contenedores

```txt
 docker compose down
```

Detener contenedores y borrar el volumen de PostgreSQL

Verificar Backend

```txt
 docker compose down -v
```

CUIDADO!! El flag -v borra toda la base de datos

## 6. Base de datos y migraciones

El backend ejecuta automaticamente
Verificar Backend

```txt
 alembic upgrade head
```

al iniciar el contenedor

Para ver las tablas creadas

```txt
docker compose exec db psql -U autospot_user -d autospot_db -c "\dt"
```

---

## 7. Backend sin Dokcer

Dedes la raiz del proyecto

```txt
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Levantar PostgreSQL con Docker

```txt
cd ..
docker compose up db -d
```

Exportar variables de entorno

```txt
set -a
source .env
set +a
```

Aplicar migraciones

```txt
cd backend
alembic upgrade head
```

Levantar FastAPI

```txt
uvicorn app.main:app --reload
```

Backend Local: http://localhost:8000
Backend Swagger: http://localhost:8000/docs

## 8. Frontend Sin Docker

```txt
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend Local

```txt
http://localhost:5173
```

## 9. Autenticación

1.  Registrar usuario: ` POST /usuarios/registro`
2.  Iniciar Sesión: ` POST /usuarios/login`
3.  Usar el acccess_token recibido de rutas protegidas: ` Authorization: Bearer <token>`
4.  Rutas protegidas pricipales:
    ```txt
    PUT   /usuarios/{usuario_id}/actualizar
    PUT   /usuarios/{usuario_id}/datos-personales
    PUT   /usuarios/{usuario_id}/datos-personales/actualizar
    POST  /usuarios/{propietario_id}/vehiculos
    GET   /usuarios/{propietario_id}/vehiculos
    PATCH /vehiculos/{vehiculo_id}/precio
    PATCH /vehiculos/{vehiculo_id}/documentacion
    POST  /usuarios/logout
    ```
    Reglas se seguridad:
    1. Un usuario solo puede operar sobre sus propios datos.
    2. Un propietario solo puede operar sobre sus propios vehículos.
    3. Las rutas sensibles requieren token JWT válido.
    4. Los tokens invalidados por logout no pueden reutilizarse.

---

## 10. CORS

En desarrollo local:

```txt
CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
```

En produccion hay que reemplazar por la URL públioca de forntend
