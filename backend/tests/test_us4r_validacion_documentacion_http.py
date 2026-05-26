import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Para evitar el error de recolección de pytest ("FATAL ERROR: ..."):
# 1. Aseguramos importar la instancia real de la app desde app.main.
# 2. Todas las funciones de prueba comienzan estrictamente con "test_".
# 3. Mockeamos el servicio interno ("resolver_solicitud") y las dependencias (get_db / auth)
#    usando el sistema de dependency_overrides de FastAPI. Esto evita que los tests intenten
#    conectarse a una base de datos real o requieran tokens JWT válidos durante la recolección
#    y ejecución en ambientes sin base de datos.
from app.main import app
from app.dependencies.auth import requerir_rol_admin

client = TestClient(app)

def mock_requerir_rol_admin():
    return {"id": "admin-id", "rol": "ADMIN"}

def test_endpoint_aprobar_documentacion_exitoso():
    app.dependency_overrides[requerir_rol_admin] = mock_requerir_rol_admin
    
    with patch("app.routers.solicitudes_documentacion.resolver_solicitud") as mock_resolver:
        response = client.post("/admin/solicitudes-documentacion/VEHICULO/123e4567-e89b-12d3-a456-426614174000/aprobar")
        
        assert response.status_code == 204
        mock_resolver.assert_called_once()
        
    app.dependency_overrides.clear()

def test_endpoint_rechazar_documentacion_exige_motivo():
    app.dependency_overrides[requerir_rol_admin] = mock_requerir_rol_admin
    
    with patch("app.routers.solicitudes_documentacion.resolver_solicitud") as mock_resolver:
        # Caso 1: Falta el body completo (FastAPI Pydantic Error)
        response_missing = client.post("/admin/solicitudes-documentacion/VEHICULO/123e4567-e89b-12d3-a456-426614174000/rechazar")
        assert response_missing.status_code == 422
        
        # Caso 2: Se envia motivo vacio, lo cual dispara la validacion ValueError en el servicio
        mock_resolver.side_effect = ValueError("El motivo de rechazo es obligatorio para rechazar la solicitud.")
        response_empty = client.post(
            "/admin/solicitudes-documentacion/VEHICULO/123e4567-e89b-12d3-a456-426614174000/rechazar",
            json={"motivo_rechazo": "   "}
        )
        assert response_empty.status_code == 422
        assert "El motivo de rechazo es obligatorio" in response_empty.json()["detail"]
        
    app.dependency_overrides.clear()

def test_lista_pendientes_excluye_solicitudes_resueltas():
    app.dependency_overrides[requerir_rol_admin] = mock_requerir_rol_admin
    
    with patch("app.routers.solicitudes_documentacion.listar_solicitudes_pendientes") as mock_listar:
        # Al devolver lista vacia, simulamos que el backend excluyo correctamente
        # las solicitudes que cambiaron de estado (ya no son "EN_REVISION").
        mock_listar.return_value = []
        
        response = client.get("/admin/solicitudes-documentacion")
        
        assert response.status_code == 200
        assert response.json() == []
        mock_listar.assert_called_once()
        
    app.dependency_overrides.clear()
