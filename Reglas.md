# Guía de trabajo para Historias de Usuario — AutoSpot

Este documento define cómo debe trabajar el equipo sobre nuevas historias de usuario y qué condiciones debe cumplir una US para considerarse completa.

La idea principal es simple:

> Una historia de usuario no está completa si solo existe en backend, solo existe en frontend o solo tiene código sin pruebas.  
> Una US completa debe funcionar de punta a punta: base de datos, backend, frontend, validaciones, tests y documentación mínima cuando corresponda.

---

# 1. Flujo de ramas

## Regla 1 — Nadie trabaja directo sobre `main`

La rama `main` representa la versión estable del proyecto.

Debe cumplir siempre:

- Levanta con Docker.
- Backend responde.
- Frontend responde.
- Tests backend pasan.
- Frontend compila.
- No contiene `.env`.

---

## Regla 2 — Nadie trabaja directo sobre `develop`, salvo merges

La rama `develop` se usa como rama de integración.

Ahí se juntan las funcionalidades terminadas antes de pasarlas a `main`.

---

## Regla 3 — Toda tarea sale desde `develop`

Antes de empezar cualquier historia, corrección o mejora:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nombre-de-la-tarea
```

Ejemplos:

```bash
git checkout -b feature/editar-vehiculo
git checkout -b feature/documentacion-auto
git checkout -b fix/login-token
git checkout -b chore/readme
```

# Regla 4

Antes de abrir un **Pull Request** hacia **develop**, correr en la raiz:

```bash
docker compose down -v
docker compose up --build -d
docker compose ps
curl -I http://localhost:8000/docs
curl -I http://localhost:3000
docker compose exec -T web pytest -v
```

y para el frontend (parado en la raíz)

```bash
cd frontend
npm install
npm run lint
npm run build
cd ..
```

Resultado esperado:

- Backend responde
- Frontend responde
- Test backend responde
- Froontend no tiene errores de lint
- Frontend compila

# Regla 5 - Antes de pasar develop a main

Antes de mergear repetir todo este checklist

```bash
git checkout develop
git pull origin develop

docker compose down -v
docker compose up --build -d
docker compose ps
curl -I http://localhost:8000/docs
curl -I http://localhost:3000
docker compose exec -T web pytest -v

cd frontend
npm install
npm run lint
npm run build
cd ..
```

### SI ALGO FALLA, NO SE MERGEA

---

---

# CUANDO UNA US ESTÁ COMPLETA:

Una US se considera completa solo si cumple todos los puntos que apliquen.

Análisis mínimo de la US

1. Qué usuario ejecuta la acción.
2. Qué datos necesita.
3. Qué validaciones existen.
4. Qué resultado espera.
5. Qué errores pueden ocurrir.
6. Qué endpoint o endpoints hacen falta.
7. Qué pantalla o componente frontend hace falta.
8. Si requiere persistencia en base de datos.
9. Si requiere migración.
10. Si requiere autenticación.
11. Si requiere autorización sobre recursos propios.
12. Es necesario actualizar algun schema ?
    (esto lo pueden usar como contexto de propmt)

Ejemplo

```text
US: Cargar documentación del auto

Actor:
Propietario.

Objetivo:
Cargar patente, chasis, motor, titular, cédula, póliza, VTV, estación y teléfono.

Backend:
PATCH /vehiculos/{vehiculo_id}/documentacion

Seguridad:
Solo el propietario del vehículo puede cargar documentación.

Base de datos:
Sí, requiere campos nuevos o tabla asociada si no existen.

Frontend:
Formulario de carga de documentación.

Tests:
Servicio + HTTP + validaciones.
```

# Checklist de Backend

Una US con backend debe incluir, cuaod correspnda

## Schema Pydantic

Ubicacion sugerida

```text
backend/app/schema/
```

Debe tener:

- Schema de entrada
- Schema de respuesta publica
- Validacion de campos
- Mneaajes de error claros

## Modelo SQLAlchemy

Ubicacion sugerida

```text
backend/app/models/
```

Se modifica o crea modelo cuando la US necesita persistir información nueva.

Ejemplos de casos donde hace falta tocar modelo:

- Nuevo campo persistente.
- Nueva entidad.
- Nueva relación entre entidades.
- Nuevo estado o atributo guardado en DB.
- Nueva tabla intermedia.

## Servicio de negocio

Ubicacion sugerida

```text
backend/app/services/
```

La lógica de negocio no debe quedar metida directamente en el router.

El servicio debe encargarse de:

- Validar reglas de negocio.
- Consultar entidades.
- Crear o actualizar datos.
- Lanzar excepciones de dominio.
- Hacer commit cuando corresponda.

## Router HTTP

Ubicacion sugerida

```text
backend/app/routers/
```

El router debe encargarse de:

- Definir endpoint.
- Recibir payload.
- Inyectar DB.
- Inyectar usuario autenticado si corresponde.
- Delegar al servicio.
- Traducir excepciones a HTTP.

No debe contener lógica de negocio pesada.

## Excepciones de dominio

Ubicacion sugerida

```text
backend/app/exceptions.py
```

## Autenticacion y autorizacion

Toda ruta sensible debe requerir JWT.

Una ruta es sensible si:

- Lee datos privados.
- Modifica datos de usuario.
- Crea datos asociados a un usuario.
- Modifica vehículos.
- Modifica documentación.
- Modifica precios.
- Depende de usuario_id, propietario_id o vehiculo_id.

No alcanza con recibir un token. También hay que validar autorización.

Ejemplo:

```text
El usuario autenticado solo puede operar sobre su propio usuario_id.
El propietario solo puede operar sobre sus propios vehículos.
```

Comandos esperados

```text
Sin token        → 401 Unauthorized
Token inválido   → 401 Unauthorized
Recurso ajeno    → 403 Forbidden
Recurso no existe → 404 Not Found
Payload inválido → 422 Unprocessable Content
```

# CUANDO HACE FALTA UNA MIGRACION ?

Una migración es necesaria cuando cambia la estructura de la base de datos.

- Se crea una tabla nueva.
- Se agrega una columna.
- Se elimina una columna.
- Se cambia el tipo de una columna.
- Se agrega una foreign key.
- Se agrega un índice.
- Se agrega una restricción unique.
- Se agrega una relación nueva.
- Se cambia un enum persistido.
- Se agregan campos persistentes a un modelo existente.

Ejemplos:

```text
Agregar precio_por_dia a Vehiculo → requiere migración.
Agregar tabla documentos_vehiculo → requiere migración.
Agregar estado_validacion a datos_personales → requiere migración.
Agregar una FK propietario_id → requiere migración.
```

Pero, como creamos una migración ?

Desde la raiz del prooyecto:

```bash
docker compose up -d db
```

Luego, entramos al backend

```bash
docker compose exec web alembic revision --autogenerate -m "Aca ponen una descripcion d elo quehicieron"
```

Luego revisan que haya saliido bien

```text
backend/alembic/versions/
```

APLICAR MIGRACION

```bash
docker compose exec web alembic upgrade head
docker compose exec web alembic current

```

Ver tablas (para ver si esta lo que creamos)

```bash
docker compose exec db psql -U autospot_user -d autospot_db -c "\dt"

```

---

---

---

# FRONTEND

## Paginas o componentes

Ubicacion sugerida

```text
frontend/src/features
```

## Servicio API

Las llamadas HTTP deben estar centralizadas en servicios, no sueltas por todos lados

Ejemplo:

```text
frontend/src/features/vehiculos/api/vehiculoService.js
```

El frontend debe usar

```text
import.meta.env.VITE_API_BASE_URL

nada de harcodeaos
```

## Manejo de token

Las rutas protegidas deben enviar

```text
Authorization: Bearer <token>
```

Si el token no existe, el frontend debe redirigir o impedir la accion

## Manejo de errores

```text
401 → sesión inválida o no iniciada
403 → no autorizado
404 → recurso no encontrado
409 → conflicto de negocio
422 → datos inválidos
500 → error inesperado
```

---

---

---

# TEST

Una US completa debe tener test

Ubicacion:

```text
backend/test
```

Debe probar:

- Caso exitoso.
- Validaciones de negocio.
- Recurso inexistente.
- Conflictos.

```text
test_define_precio_por_dia_valido_en_vehiculo_existente
test_precio_por_dia_menor_o_igual_a_cero_es_invalido
test_no_define_precio_si_vehiculo_no_existe
```

## Test HTTP

Deben probar el contrato real de la API

```text
200 / 201 → operación exitosa
401 → sin token si la ruta es protegida
403 → recurso ajeno si aplica
404 → recurso inexistente
409 → conflicto si aplica
422 → payload inválido
```
