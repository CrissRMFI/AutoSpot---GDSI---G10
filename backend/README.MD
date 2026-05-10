# AutoSpot - Sistema de Gestion de Alquiler de Vehiculos 

Este es el backend del proyecto AutoSpot para la materia GDSI (FIUBA). El sistema utiliza una arquitectura basada en microservicios/modulos para gestionar la logistica de alquiler de autos mediante estaciones fisicas.

## Stack Tecnologico
* **Lenguaje:** Python 3.12+
* **Framework:** FastAPI
* **ORM:** SQLAlchemy
* **Base de Datos:** PostgreSQL
* **Testing:** pytest
* **Migraciones:** Alembic

---

## Configuracion del Entorno de Desarrollo

Dentro de la carpeta backend, crea y activa el entorno:
# Crear el entorno
python -m venv venv

# Activar el entorno
.\\venv\\Scripts\\activate 

### En Windows (PowerShell)

Si es la primera vez que ejecutas scripts en PowerShell, abrilo como administrador y otorga permisos:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Luego crea y activa el entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

---

### En Ubuntu / Linux (Bash)

Asegurate de tener instalada la version 3.12 de Python y el paquete venv:

```bash
sudo apt install python3.12-venv
```

Luego crea y activa el entorno virtual:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

---

## 3. Instalar Dependencias

Una vez que veas el prefijo (venv)` en la terminal, instala todas las dependencias necesarias:

pip install -r requirements.txt