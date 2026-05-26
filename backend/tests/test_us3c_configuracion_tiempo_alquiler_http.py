"""
Tests de Integración HTTP — US 3C: Configuracion del tiempo de alquiler.

Metodología: TDD (Fase Roja).

Endpoint imaginado para TDD:
  POST /alquiler/simular-tiempo

Criterios de Aceptación cubiertos en esta suite:
    CA 1: Dado que el negocio establece un tiempo minimo de uso (1 dia),
          cuando el periodo definido entre el inicio y el fin es inferior a dicho umbral,
          entonces el sistema debe rechazar la solicitud (HTTP 422).
    CA 2: Dado que se ha definido un periodo valido y coherente,
          cuando el sistema procesa la solicitud,
          entonces debe determinar la duracion total exacta, en horas y dias (HTTP 200).
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
# Importamos el client fixture para poder hacer peticiones
from tests.conftest import client  # noqa: F401


_ENDPOINT = "/alquiler/simular-tiempo"


class TestCA1_TiempoMinimoAlquilerHTTP:
    """Verifica que HTTP rechaza periodos inferiores a 1 día."""

    def test_ca1_tiempo_menor_a_un_dia_devuelve_422(self, client: TestClient):
        """Un periodo menor a 24hs debe retornar HTTP 422 y un mensaje claro."""
        inicio = datetime(2025, 5, 1, 10, 0, 0)
        # 12 horas de alquiler
        fin = inicio + timedelta(hours=12)

        payload = {
            "fecha_inicio": inicio.isoformat(),
            "fecha_fin": fin.isoformat()
        }

        response = client.post(_ENDPOINT, json=payload)

        assert response.status_code == 422, f"Esperaba 422, obtuve {response.status_code}"
        
        # Validar el mensaje de error del negocio devuelto en detail
        body = response.json()
        detalles = str(body.get("detail", ""))
        assert "minimo de alquiler es de 1 dia" in detalles or "1 dia" in detalles, (
            f"Mensaje de error inesperado: {detalles}"
        )


class TestCA2_DuracionTotalExactaHTTP:
    """Verifica que el cálculo exacto de días y horas se devuelve en la respuesta."""

    def test_ca2_calculo_dias_y_horas_devuelve_200(self, client: TestClient):
        """Periodo válido devuelve 200 OK con 'dias' y 'horas' en la respuesta."""
        inicio = datetime(2025, 5, 1, 10, 0, 0)
        # 2 días y 4 horas
        fin = inicio + timedelta(days=2, hours=4)

        payload = {
            "fecha_inicio": inicio.isoformat(),
            "fecha_fin": fin.isoformat()
        }

        response = client.post(_ENDPOINT, json=payload)

        assert response.status_code == 200, f"Esperaba 200, obtuve {response.status_code}. Body: {response.text}"
        
        data = response.json()
        assert "dias" in data
        assert "horas" in data
        assert data["dias"] == 2
        assert data["horas"] == 4

    def test_fechas_invalidas_devuelven_422(self, client: TestClient):
        """Si la fecha de fin es anterior a la fecha de inicio debe rechazar."""
        inicio = datetime(2025, 5, 2, 10, 0, 0)
        fin = datetime(2025, 5, 1, 10, 0, 0)  # Un dia antes

        payload = {
            "fecha_inicio": inicio.isoformat(),
            "fecha_fin": fin.isoformat()
        }

        response = client.post(_ENDPOINT, json=payload)

        assert response.status_code == 422
