from fastapi import APIRouter
from app.schemas.ia import DatosVehiculoIA, SugerenciaPrecioIA
from app.services import ia_service

router = APIRouter(prefix="/ia", tags=["IA"])

@router.post("/generar-precio", response_model=SugerenciaPrecioIA)
async def generar_precio_vehiculo(datos: DatosVehiculoIA):
    """
    Recibe las características de un vehículo y devuelve una sugerencia
    de precios (mínimo, recomendado y máximo) generada por Google Gemini.
    """
    return await ia_service.generar_sugerencia_precio(datos)
