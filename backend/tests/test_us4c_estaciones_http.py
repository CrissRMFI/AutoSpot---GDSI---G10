"""
Tests de Integración HTTP — US 4C: Visualización y selección de estación.

Metodología: TDD (Fase Verde - Integración).

Criterios de Aceptación:
    CA 1: La solicitud de exploración incluye únicamente Estaciones activas.
    CA 2 (Listado): El sistema incluye las Estaciones en una lista.
    CA 3: Al seleccionar un punto de retiro específico, se suministra la dirección y las instrucciones de acceso para el Activo.
"""
import pytest
from fastapi.testclient import TestClient

from app.models.estacion import Estacion
from app.database import SessionLocal


_ENDPOINT_ESTACIONES = "/estaciones"


@pytest.fixture(scope="function", autouse=True)
def setup_estaciones_db():
    db = SessionLocal()
    
    # 1. Limpiar estado previo
    db.query(Estacion).delete()
    
    # 2. Insertar data de prueba respetando el Lenguaje Ubicuo (Estación, Activo)
    estaciones = [
        Estacion(
            id=1, nombre="Estación Palermo", direccion="Honduras 5500", 
            instrucciones_acceso="Retiro keyless en subsuelo", zona="Palermo", activa=True
        ),
        Estacion(
            id=2, nombre="Estación Recoleta", direccion="Av. Callao 1000", 
            instrucciones_acceso="Ingreso por rampa vehicular", zona="Recoleta", activa=True
        ),
        Estacion(
            id=3, nombre="Estación Mantenimiento", direccion="Taller Central", 
            instrucciones_acceso="Prohibido el paso de Conductores", zona="Talleres", activa=False
        )
    ]
    
    db.add_all(estaciones)
    db.commit()
    
    yield
    
    # 3. Teardown
    db.query(Estacion).delete()
    db.commit()
    db.close()


class TestCA1yCA2_ListarEstacionesActivasHTTP:
    """
    Verifica que el sistema procesa la solicitud de exploración devolviendo
    una lista (CA2) que incluye únicamente aquellas estaciones operativas (CA1).
    """

    def test_listar_estaciones_devuelve_lista_solo_activas(self, client: TestClient):
        response = client.get(f"{_ENDPOINT_ESTACIONES}/")
        
        assert response.status_code == 200
        data = response.json()
        
        # CA 2: El sistema debe incluir las estaciones en formato lista
        assert isinstance(data, list)
        
        # CA 1: Excluyendo puntos inhabilitados (deben ser 2 de las 3 insertadas)
        assert len(data) == 2
        
        # Validar exhaustivamente que el booleano 'activa' sea True
        for estacion in data:
            assert estacion["activa"] is True


class TestCA3_DetalleEstacionHTTP:
    """
    Verifica que al acceder a la información de la estación, el sistema suministra
    la dirección exacta y las instrucciones de acceso necesarias para el Conductor.
    """

    def test_obtener_detalle_estacion_existente_devuelve_200(self, client: TestClient):
        # Solicitamos la Estación Palermo (id=1)
        response = client.get(f"{_ENDPOINT_ESTACIONES}/1")
        
        assert response.status_code == 200
        data = response.json()
        
        # CA 3: Suministra la dirección y las instrucciones de acceso
        assert data["id"] == 1
        assert data["direccion"] == "Honduras 5500"
        assert data["instrucciones_acceso"] == "Retiro keyless en subsuelo"

    def test_obtener_detalle_estacion_inexistente_devuelve_404(self, client: TestClient):
        response = client.get(f"{_ENDPOINT_ESTACIONES}/999")
        
        assert response.status_code == 404
        assert response.json() == {"detail": "Estación no encontrada"}

    def test_obtener_detalle_estacion_inactiva_devuelve_404(self, client: TestClient):
        # La estación 3 existe pero está inactiva (Mantenimiento)
        response = client.get(f"{_ENDPOINT_ESTACIONES}/3")
        
        assert response.status_code == 404
        assert response.json() == {"detail": "La estación no está activa"}