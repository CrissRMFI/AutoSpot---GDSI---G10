# Regla 1:

Nadie trabaja directo sobre **main**

# Regla 2:

Nadie trabaja directo sobre la rama **develop**, salvo merges

# Regla 3:

Toda tarea sale desde **develop**

```text
git checkout develop
git pull origin develop
git checkout -b feature/nombre-de-la-tarea

```

# Regla 4

Antes de pedir un merge a **develop correr**

```text
docker compose down -v
docker compose up --build -d
docker compose exec -T web pytest -v
```

y para el frontend (parado en la raíz)

```text
cd frontend
npm install
npm run lint
npm run build
```

# Regla 5:

Antes de pasar develop a main, repetir todo el checklist
