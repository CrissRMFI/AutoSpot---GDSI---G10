import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.estacion import Estacion
from app.database import Base, engine, SessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Limpiar
    db.query(Estacion).delete()
    
    # Crear data de prueba
    estacion1 = Estacion(id=1, nombre="Estacion A", direccion="Dir A", instrucciones_acceso="Inst A", zona="Zona A", activa=True)
    estacion2 = Estacion(id=2, nombre="Estacion B", direccion="Dir B", instrucciones_acceso="Inst B", zona="Zona B", activa=True)
    estacion_inactiva = Estacion(id=3, nombre="Estacion Inactiva", direccion="Dir C", instrucciones_acceso="Inst C", zona="Zona C", activa=False)
    
    db.add_all([estacion1, estacion2, estacion_inactiva])
    db.commit()
    
    yield
    
    db.query(Estacion).delete()
    db.commit()
    db.close()


def test_get_estaciones_returns_200_and_list(setup_db):
    response = client.get("/estaciones/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Deben haber 2 estaciones activas
    assert len(data) == 2


def test_get_estaciones_only_active(setup_db):
    response = client.get("/estaciones/")
    data = response.json()
    for est in data:
        assert est["activa"] is True


def test_get_estacion_detail_success(setup_db):
    response = client.get("/estaciones/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["direccion"] == "Dir A"
    assert data["instrucciones_acceso"] == "Inst A"


def test_get_estacion_detail_not_found():
    response = client.get("/estaciones/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Estación no encontrada"


def test_get_estacion_detail_inactiva(setup_db):
    response = client.get("/estaciones/3")
    assert response.status_code == 404
    assert response.json()["detail"] == "La estación no está activa"
