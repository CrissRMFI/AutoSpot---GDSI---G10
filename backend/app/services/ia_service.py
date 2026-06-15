import os
import json
import logging
import google.generativeai as genai

from fastapi import HTTPException
from app.schemas.ia import DatosVehiculoIA, SugerenciaPrecioIA

logger = logging.getLogger(__name__)

# Intentamos configurar la API Key de forma global
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

async def generar_sugerencia_precio(datos: DatosVehiculoIA) -> SugerenciaPrecioIA:
    """
    Se comunica con la API de Google Gemini para obtener una sugerencia de precio
    por día para el alquiler de un vehículo, basándose en sus características.
    """
    if not GEMINI_API_KEY:
        # Modo Mock / Fallback si no hay API Key configurada
        # Para que no bloquee el desarrollo en local si no se ha configurado la variable de entorno.
        logger.warning("No GEMINI_API_KEY set. Returning mock data.")
        return SugerenciaPrecioIA(
            precio_minimo=15000.0,
            precio_recomendado=25000.0,
            precio_maximo=35000.0,
            resumen="[MOCK] Basado en los datos ingresados, se estima un valor competitivo en el mercado actual considerando el año y la categoría del vehículo. Configura tu API Key de Gemini en el backend para obtener estimaciones reales."
        )

    # Inicializamos el modelo (usamos gemini-3.1-flash-lite según requerimiento)
    try:
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        
        # --- PROMPT PARA LA IA ---
        # Puedes modificar este prompt libremente para ajustar el comportamiento y tono de la IA.
        prompt = f"""
Eres un tasador experto de vehículos en Argentina para una plataforma de alquiler peer-to-peer llamada AutoSpot.
El usuario quiere publicar el siguiente vehículo y necesita que le sugieras un precio de alquiler diario en pesos argentinos (ARS).

Datos del vehículo:
- Marca: {datos.marca}
- Modelo: {datos.modelo}
- Año: {datos.anio}
- Transmisión: {datos.tipo_transmision}
- Capacidad (pasajeros): {datos.capacidad}
- Categoría: {datos.categoria}
- Combustible: {datos.tipo_combustible}
- Pet Friendly: {"Sí" if datos.pets_friendly else "No"}

Debes devolver UNICAMENTE un objeto JSON con la siguiente estructura, sin markdown ni backticks adicionales:
{{
  "precio_minimo": 0.0,
  "precio_recomendado": 0.0,
  "precio_maximo": 0.0,
  "resumen": "string"
}}

El "resumen" debe ser una explicación corta (máximo 3 oraciones) dirigida al propietario explicando por qué se le recomienda ese precio basado en las características de su vehículo.
"""
        # Ejecutamos la petición a la API
        response = model.generate_content(prompt)
        
        try:
            text_response = response.text.strip()
        except ValueError as ve:
            # Esto pasa si la respuesta fue bloqueada por safety settings
            raise Exception(f"Respuesta bloqueada por filtros de seguridad: {str(ve)}")
            
        import re
        # Extraer solo el bloque JSON por si viene texto extra alrededor
        match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if match:
            clean_json = match.group(0)
        else:
            clean_json = text_response
            
        try:
            parsed_json = json.loads(clean_json.strip())
        except json.JSONDecodeError as e:
            raise Exception(f"La IA no devolvió un JSON válido. Respuesta cruda: {text_response}")
        
        return SugerenciaPrecioIA(
            precio_minimo=float(parsed_json.get("precio_minimo", 0)),
            precio_recomendado=float(parsed_json.get("precio_recomendado", 0)),
            precio_maximo=float(parsed_json.get("precio_maximo", 0)),
            resumen=parsed_json.get("resumen", "")
        )
        
    except Exception as e:
        logger.error(f"Error al generar precio con IA: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno de la IA: {str(e)}"
        )
