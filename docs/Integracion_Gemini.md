# Integración con Google Gemini (IA de Precios)

Se ha implementado una nueva funcionalidad que permite sugerir al propietario un precio de alquiler diario basado en las características de su vehículo. Para lograr esto, se utiliza el modelo `gemini-1.5-flash` de Google.

A continuación se detallan los pasos necesarios para configurar y probar esta integración en el backend.

## 1. Obtener la API Key de Gemini

Si aún no tienes una clave de API:
1. Dirígete a [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Inicia sesión con tu cuenta de Google.
3. Haz clic en el botón **"Create API Key"**.
4. Copia la clave generada. Esta clave es secreta y no debe subirse a repositorios públicos.

## 2. Configurar la API Key en el Entorno Local

En la raíz del proyecto backend (`backend/`), deberías tener un archivo `.env` (puedes basarte en `.env.example`).
Añade la siguiente línea al final del archivo:

```env
GEMINI_API_KEY="tu_clave_api_copiada_aqui"
```

> **Nota:** Si la variable `GEMINI_API_KEY` no está configurada, el backend utilizará automáticamente un "modo mock" (simulación), devolviendo precios estáticos predefinidos (min 15000, rec 25000, max 35000) para evitar que el desarrollo se bloquee.

## 3. Instalar las Dependencias

Ya se ha agregado `google-generativeai` al archivo `requirements.txt`. Para asegurarte de tenerlo instalado en tu entorno virtual:

1. Ingresa a la carpeta `backend`.
2. Activa tu entorno virtual (por ejemplo, `source venv/bin/activate`).
3. Instala los requerimientos actualizados:
   ```bash
   pip install -r requirements.txt
   ```

## 4. Estructura de la Implementación

Si deseas modificar el **prompt** que se le envía a la IA (para cambiar el tono, las reglas de cálculo o pedir más detalles), puedes hacerlo editando el siguiente archivo:

- **Ruta del Servicio:** `backend/app/services/ia_service.py`
  - *Aquí encontrarás la variable `prompt` donde se define la instrucción para Gemini.*

Las demás piezas involucradas son:
- **Router:** `backend/app/routers/ia.py` (expone el endpoint `POST /ia/generar-precio`).
- **Esquemas:** `backend/app/schemas/ia.py` (define la validación de entrada/salida).

Con esto configurado, el botón "Generar precio" en el frontend comenzará a enviar datos reales al modelo de Google Gemini y renderizará el slider con los resultados auténticos.
