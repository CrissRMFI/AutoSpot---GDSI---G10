"""
Tests de integración HTTP para la US 15C: Check-in de Vehículo.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.dependencies.auth import get_usuario_actual

client = TestClient(app)

def mock_get_usuario_actual():
    return {"id": "123e4567-e89b-12d3-a456-426614174000", "rol": "CLIENTE"}

def test_crear_checkin_endpoint_exitoso():
    app.dependency_overrides[get_usuario_actual] = mock_get_usuario_actual
    
    payload = {
        "reserva_id": "999e4567-e89b-12d3-a456-426614174999",
        "nivel_combustible": "Lleno",
        "kilometraje_actual": 12000,
        "esta_limpio": True,
        "tiene_danios": False,
        "url_foto_frente": "frente.jpg",
        "url_foto_trasera": "trasera.jpg",
        "url_foto_lateral_izq": "izq.jpg",
        "url_foto_lateral_der": "der.jpg",
        "url_foto_panel": "panel.jpg",
        "urls_fotos_danios": []
    }
    
    with patch("app.routers.checkins.crear_checkin") as mock_service:
        # Mocking the returned object to behave like a CheckinVehiculo
        mock_service.return_value.id = uuid.uuid4()
        mock_service.return_value.reserva_id = uuid.UUID(payload["reserva_id"])
        mock_service.return_value.conductor_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_service.return_value.estado = "PENDIENTE"
        mock_service.return_value.motivo_rechazo = None
        mock_service.return_value.created_at = "2024-01-01T00:00:00Z"
        mock_service.return_value.updated_at = "2024-01-01T00:00:00Z"
        mock_service.return_value.nivel_combustible = "Lleno"
        mock_service.return_value.kilometraje_actual = 12000
        mock_service.return_value.esta_limpio = True
        mock_service.return_value.tiene_danios = False
        mock_service.return_value.descripcion_danios = None
        mock_service.return_value.url_foto_frente = "frente.jpg"
        mock_service.return_value.url_foto_trasera = "trasera.jpg"
        mock_service.return_value.url_foto_lateral_izq = "izq.jpg"
        mock_service.return_value.url_foto_lateral_der = "der.jpg"
        mock_service.return_value.url_foto_panel = "panel.jpg"
        mock_service.return_value.urls_fotos_danios = []
        mock_service.return_value.url_foto_extra = None
        mock_service.return_value.notas_adicionales = None

        response = client.post("/checkins", json=payload)
        
        assert response.status_code == 201
        assert response.json()["estado"] == "PENDIENTE"
        mock_service.assert_called_once()
        
    app.dependency_overrides.clear()

def test_re_enviar_checkin_endpoint_exitoso():
    app.dependency_overrides[get_usuario_actual] = mock_get_usuario_actual
    checkin_id = str(uuid.uuid4())
    
    payload = {
        "nivel_combustible": "1/2",
        "kilometraje_actual": 12010,
        "esta_limpio": True,
        "tiene_danios": False,
        "url_foto_frente": "frente.jpg",
        "url_foto_trasera": "trasera.jpg",
        "url_foto_lateral_izq": "izq.jpg",
        "url_foto_lateral_der": "der.jpg",
        "url_foto_panel": "panel.jpg",
        "urls_fotos_danios": []
    }
    
    with patch("app.routers.checkins.re_enviar_checkin") as mock_service:
        mock_service.return_value.id = uuid.UUID(checkin_id)
        mock_service.return_value.reserva_id = uuid.uuid4()
        mock_service.return_value.conductor_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_service.return_value.estado = "PENDIENTE"
        mock_service.return_value.motivo_rechazo = None
        mock_service.return_value.created_at = "2024-01-01T00:00:00Z"
        mock_service.return_value.updated_at = "2024-01-01T00:00:00Z"
        mock_service.return_value.nivel_combustible = "1/2"
        mock_service.return_value.kilometraje_actual = 12010
        mock_service.return_value.esta_limpio = True
        mock_service.return_value.tiene_danios = False
        mock_service.return_value.descripcion_danios = None
        mock_service.return_value.url_foto_frente = "frente.jpg"
        mock_service.return_value.url_foto_trasera = "trasera.jpg"
        mock_service.return_value.url_foto_lateral_izq = "izq.jpg"
        mock_service.return_value.url_foto_lateral_der = "der.jpg"
        mock_service.return_value.url_foto_panel = "panel.jpg"
        mock_service.return_value.urls_fotos_danios = []
        mock_service.return_value.url_foto_extra = None
        mock_service.return_value.notas_adicionales = None

        response = client.put(f"/checkins/{checkin_id}", json=payload)
        
        assert response.status_code == 200
        assert response.json()["estado"] == "PENDIENTE"
        mock_service.assert_called_once()
        
    app.dependency_overrides.clear()


def test_obtener_mi_checkin_de_reserva_endpoint_exitoso():
    app.dependency_overrides[get_usuario_actual] = mock_get_usuario_actual
    reserva_id = str(uuid.uuid4())

    with patch("app.routers.checkins.obtener_checkin_de_reserva_conductor") as mock_service:
        mock_service.return_value.id = uuid.uuid4()
        mock_service.return_value.reserva_id = uuid.UUID(reserva_id)
        mock_service.return_value.conductor_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_service.return_value.estado = "PENDIENTE"
        mock_service.return_value.motivo_rechazo = None
        mock_service.return_value.created_at = "2024-01-01T00:00:00Z"
        mock_service.return_value.updated_at = "2024-01-01T00:00:00Z"
        mock_service.return_value.nivel_combustible = "Lleno"
        mock_service.return_value.kilometraje_actual = 12000
        mock_service.return_value.esta_limpio = True
        mock_service.return_value.tiene_danios = False
        mock_service.return_value.descripcion_danios = None
        mock_service.return_value.url_foto_frente = "frente.jpg"
        mock_service.return_value.url_foto_trasera = "trasera.jpg"
        mock_service.return_value.url_foto_lateral_izq = "izq.jpg"
        mock_service.return_value.url_foto_lateral_der = "der.jpg"
        mock_service.return_value.url_foto_panel = "panel.jpg"
        mock_service.return_value.urls_fotos_danios = []
        mock_service.return_value.url_foto_extra = None
        mock_service.return_value.notas_adicionales = None

        response = client.get(f"/checkins/reservas/{reserva_id}")

        assert response.status_code == 200
        assert response.json()["reserva_id"] == reserva_id
        assert response.json()["estado"] == "PENDIENTE"
        mock_service.assert_called_once()

    app.dependency_overrides.clear()


def test_obtener_mi_checkin_de_reserva_endpoint_sin_checkin_devuelve_404():
    app.dependency_overrides[get_usuario_actual] = mock_get_usuario_actual
    reserva_id = str(uuid.uuid4())

    with patch("app.routers.checkins.obtener_checkin_de_reserva_conductor", return_value=None):
        response = client.get(f"/checkins/reservas/{reserva_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Check-in no encontrado."

    app.dependency_overrides.clear()
