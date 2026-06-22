import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import MagicMock

from app.models.reporte import Reporte
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.models.vehiculo import Vehiculo
from app.services.incidente_service import buscar_incidentes, obtener_incidente_detalle

@pytest.fixture
def mock_db():
    return MagicMock()

def test_buscar_incidentes_sin_filtros(mock_db):
    """Prueba que buscar_incidentes retorne los resultados correctamente mapeados."""
    # Setup
    r_id = uuid.uuid4()
    mock_reporte = Reporte(
        id=r_id,
        created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        estado="ACTIVO",
    )
    mock_reserva = Reserva(codigo="AX5T")
    mock_conductor = Usuario(id=uuid.uuid4())
    mock_conductor_datos = DatosPersonalesUsuario(nombre="Juan", apellido="Perez")
    mock_vehiculo = Vehiculo(marca="Toyota", modelo="Corolla", patente="AB123CD")
    
    mock_reporte.reserva = mock_reserva
    mock_reporte.conductor = mock_conductor
    mock_reporte.vehiculo = mock_vehiculo

    def side_effect_scalar(stmt):
        return mock_conductor_datos

    mock_db.scalar.side_effect = side_effect_scalar
    mock_db.scalars.return_value.all.return_value = [mock_reporte]

    resultados = buscar_incidentes(mock_db)

    assert len(resultados) == 1
    assert resultados[0]["id"] == r_id
    assert resultados[0]["codigo_reserva"] == "AX5T"
    assert resultados[0]["estado"] == "ACTIVO"
    assert resultados[0]["auto"]["patente"] == "AB123CD"
    assert resultados[0]["conductor"]["nombre"] == "Juan"


def test_obtener_incidente_detalle_exito(mock_db):
    """Prueba obtener el detalle con propietario."""
    r_id = uuid.uuid4()
    mock_reporte = Reporte(
        id=r_id,
        created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        estado="ACTIVO",
        descripcion="Choque",
    )
    mock_reserva = Reserva(codigo="AX5T")
    
    c_id = uuid.uuid4()
    mock_conductor = Usuario(id=c_id)
    mock_conductor_datos = DatosPersonalesUsuario(nombre="Juan", apellido="Perez")
    
    p_id = uuid.uuid4()
    mock_vehiculo = Vehiculo(marca="Toyota", modelo="Corolla", patente="AB123CD", propietario_id=p_id)
    
    mock_reporte.reserva = mock_reserva
    mock_reporte.conductor = mock_conductor
    mock_reporte.vehiculo = mock_vehiculo
    mock_reporte.fotos = []

    mock_propietario_datos = DatosPersonalesUsuario(nombre="Maria", apellido="Gomez")
    mock_db.scalar.side_effect = [mock_reporte, mock_propietario_datos, mock_conductor_datos]

    detalle = obtener_incidente_detalle(mock_db, r_id)

    assert detalle is not None
    assert detalle["id"] == r_id
    assert detalle["descripcion"] == "Choque"
    assert detalle["propietario"]["nombre"] == "Maria"
    assert detalle["propietario"]["apellido"] == "Gomez"
    assert detalle["fotos"] == []


def test_obtener_incidente_detalle_no_encontrado(mock_db):
    mock_db.scalar.return_value = None
    detalle = obtener_incidente_detalle(mock_db, uuid.uuid4())
    assert detalle is None
