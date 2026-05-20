"""
Script para poblar la base de datos con Estaciones (US 4C).
Ejecutar desde la raíz del backend con: python -m app.utils.seed_estaciones
"""

import sys
import os

# Asegurar que el path incluya el directorio raíz del backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.estacion import Estacion

ESTACIONES_SEED = [
    {
        "nombre": "Estación Palermo Hollywood",
        "direccion": "Honduras 5500, Palermo, CABA",
        "instrucciones_acceso": "El vehículo se encuentra en el 1er subsuelo, cochera 4. Acceso peatonal por puerta principal con el código 4455.",
        "zona": "Palermo",
        "activa": True
    },
    {
        "nombre": "Estación Soho Tech",
        "direccion": "Gurruchaga 1700, Palermo, CABA",
        "instrucciones_acceso": "Cochera descubierta en planta baja. Ingresar por el portón automático, el control está en la guantera.",
        "zona": "Palermo",
        "activa": True
    },
    {
        "nombre": "Estación San Telmo Sur",
        "direccion": "Defensa 1200, San Telmo, CABA",
        "instrucciones_acceso": "Estacionamiento privado. Avisar al guardia que retira un vehículo de AutoSpot y mostrar la confirmación en la app.",
        "zona": "San Telmo",
        "activa": True
    },
    {
        "nombre": "Estación Belgrano R",
        "direccion": "La Pampa 3100, Belgrano, CABA",
        "instrucciones_acceso": "Subsuelo 2, espacio B12. Acceso por rampa. La llave física está en el locker 3 de la entrada.",
        "zona": "Belgrano",
        "activa": True
    },
    {
        "nombre": "Estación Recoleta Mall",
        "direccion": "Vicente López 2050, Recoleta, CABA",
        "instrucciones_acceso": "Nivel -3 del shopping. Sector verde. La barrera se levanta automáticamente por lectura de patente.",
        "zona": "Recoleta",
        "activa": True
    },
    {
        "nombre": "Estación Villa Crespo Centro",
        "direccion": "Av. Corrientes 5200, Villa Crespo, CABA",
        "instrucciones_acceso": "Cochera 15 en planta baja. Retirar llave del buzón de seguridad usando el PIN 1984.",
        "zona": "Villa Crespo",
        "activa": True
    },
    {
        "nombre": "Estación Puerto Madero Diques",
        "direccion": "Alicia Moreau de Justo 1100, Puerto Madero, CABA",
        "instrucciones_acceso": "Cochera techada frente al dique 3. Espacios exclusivos AutoSpot señalizados en azul.",
        "zona": "Puerto Madero",
        "activa": True
    },
    {
        "nombre": "Estación Microcentro Obelisco",
        "direccion": "Carlos Pellegrini 400, San Nicolás, CABA",
        "instrucciones_acceso": "Subsuelo del edificio. Presentar DNI en recepción para que habiliten el ascensor a las cocheras.",
        "zona": "San Nicolás",
        "activa": True
    },
    {
        "nombre": "Estación Núñez Libertador",
        "direccion": "Av. del Libertador 7800, Núñez, CABA",
        "instrucciones_acceso": "Cochera exterior, lote 8. Acceso directo desde la avenida.",
        "zona": "Núñez",
        "activa": True
    },
    {
        "nombre": "Estación Caballito Parque",
        "direccion": "Av. Rivadavia 4900, Caballito, CABA",
        "instrucciones_acceso": "Garage privado 24hs. Preguntar por el encargado del turno y mencionar la reserva AutoSpot.",
        "zona": "Caballito",
        "activa": True
    },
    {
        "nombre": "Estación Inactiva Mantenimiento",
        "direccion": "Calle Falsa 123, Flores, CABA",
        "instrucciones_acceso": "Estación cerrada por obras.",
        "zona": "Flores",
        "activa": False
    }
]

def run_seed():
    db: Session = SessionLocal()
    try:
        # Verificar si ya existen estaciones
        count = db.query(Estacion).count()
        if count > 0:
            print(f"Ya existen {count} estaciones en la base de datos. Saltando seed.")
            return

        for data in ESTACIONES_SEED:
            nueva_estacion = Estacion(**data)
            db.add(nueva_estacion)
        
        db.commit()
        print("✅ 11 estaciones insertadas exitosamente (10 activas, 1 inactiva).")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al insertar estaciones: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando carga de datos (Seed Estaciones)...")
    run_seed()
