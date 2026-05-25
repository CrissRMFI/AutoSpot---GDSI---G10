"""
Lógica de negocio para la gestión de alquileres.
"""
from datetime import datetime
from math import floor

def calcular_tiempo_alquiler(inicio: datetime, fin: datetime) -> dict:
    """
    Calcula la duración exacta de un periodo de alquiler en días y horas.
    
    Reglas de negocio:
      - CA1: El tiempo mínimo de alquiler es de 1 día (24 horas).
      - CA2: Calcula la duración en días y horas exactas.
      
    Args:
        inicio (datetime): Fecha y hora de inicio.
        fin (datetime): Fecha y hora de fin.
        
    Returns:
        dict: Diccionario con 'dias' y 'horas'.
        
    Raises:
        ValueError: Si la duración es menor a 1 día o las fechas son incoherentes.
    """
    if fin < inicio:
        raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        
    diferencia = fin - inicio
    
    # 86400 segundos = 24 horas
    if diferencia.total_seconds() < 86400:
        raise ValueError("El tiempo minimo de alquiler es de 1 dia")
        
    dias = diferencia.days
    segundos_restantes = diferencia.seconds
    horas = floor(segundos_restantes / 3600)
    
    return {
        "dias": dias,
        "horas": horas
    }
