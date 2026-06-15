import asyncio
from dotenv import load_dotenv
load_dotenv() # make sure to load env
from app.schemas.ia import DatosVehiculoIA
from app.services.ia_service import generar_sugerencia_precio

async def main():
    datos = DatosVehiculoIA(
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        tipo_transmision="AUTOMATICA",
        capacidad=5,
        categoria="SEDAN",
        tipo_combustible="NAFTA",
        pets_friendly=True
    )
    try:
        res = await generar_sugerencia_precio(datos)
        print("SUCCESS:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
