import uuid
import pytest
from unittest.mock import patch

from app.main import app
from app.dependencies.auth import requerir_rol_admin

@pytest.fixture
def mock_admin_auth():
    """Simula un login de administrador mediante dependency overrides."""
    app.dependency_overrides[requerir_rol_admin] = lambda: {"id": str(uuid.uuid4()), "rol": "ADMIN"}
    yield
    app.dependency_overrides.clear()

@patch("app.routers.incidentes.buscar_incidentes")
def test_listar_incidentes_admin_http(mock_buscar, client, mock_admin_auth):
    """Verifica el endpoint GET /admin/incidentes con filtros vacios."""
    
    mock_buscar.return_value = [
        {
            "id": uuid.uuid4(),
            "codigo_reserva": "AX5T",
            "fecha": "2023-01-01T00:00:00Z",
            "estado": "ACTIVO",
            "auto": {"marca": "Toyota", "modelo": "Corolla", "patente": "AB123CD"},
            "conductor": {"nombre": "Juan", "apellido": "Perez"},
        }
    ]

    response = client.get("/admin/incidentes")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["codigo_reserva"] == "AX5T"
    assert data[0]["estado"] == "ACTIVO"
    assert data[0]["auto"]["patente"] == "AB123CD"
    
    # Verifica que el mock fue llamado
    mock_buscar.assert_called_once()


@patch("app.routers.incidentes.obtener_incidente_detalle")
def test_obtener_incidente_admin_http_exito(mock_detalle, client, mock_admin_auth):
    """Verifica el endpoint GET /admin/incidentes/{id} (200)."""
    
    incidente_id = uuid.uuid4()
    mock_detalle.return_value = {
        "id": incidente_id,
        "codigo_reserva": "AX5T",
        "fecha": "2023-01-01T00:00:00Z",
        "estado": "ACTIVO",
        "descripcion": "Problemas",
        "auto": {"marca": "Toyota", "modelo": "Corolla", "patente": "AB123CD"},
        "conductor": {"nombre": "Juan", "apellido": "Perez"},
        "propietario": {"nombre": "Maria", "apellido": "Gomez"},
        "fotos": []
    }

    response = client.get(f"/admin/incidentes/{incidente_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["codigo_reserva"] == "AX5T"
    assert data["descripcion"] == "Problemas"
    assert data["propietario"]["nombre"] == "Maria"


@patch("app.routers.incidentes.obtener_incidente_detalle")
def test_obtener_incidente_admin_http_404(mock_detalle, client, mock_admin_auth):
    """Verifica que el endpoint detalle devuelva 404 si no existe."""
    mock_detalle.return_value = None

    response = client.get(f"/admin/incidentes/{uuid.uuid4()}")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Incidente no encontrado"
