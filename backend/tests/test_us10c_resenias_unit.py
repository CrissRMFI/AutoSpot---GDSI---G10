import uuid
from unittest.mock import MagicMock
from datetime import datetime

import pytest

from app.services.vehiculo import obtener_resenias_vehiculo
from app.exceptions import VehiculoNoEncontradoError
from app.models.vehiculo import Vehiculo
from app.models.valoracion import Valoracion
from app.models.testimonio import Testimonio
from app.models.datos_personales_usuario import DatosPersonalesUsuario

def test_obtener_resenias_con_datos():
    """
    Simula que el vehículo existe y tiene reseñas en la DB.
    Verifica que se devuelva una lista de diccionarios con el formato correcto.
    """
    db_mock = MagicMock()
    query_vehiculo = MagicMock()
    query_resenias = MagicMock()
    db_mock.query.side_effect = [query_vehiculo, query_resenias]
    vehiculo_id = uuid.uuid4()
    
    # Mock para la primera query que verifica el vehículo
    query_vehiculo.filter.return_value.first.return_value = Vehiculo(id=vehiculo_id)
    
    # Preparamos datos simulados para el join
    reserva_id = uuid.uuid4()
    fecha_val = datetime.now()
    
    val_mock = Valoracion(reserva_id=reserva_id, vehiculo_id=vehiculo_id, puntaje=5, created_at=fecha_val)
    test_mock = Testimonio(reserva_id=reserva_id, descripcion="Excelente auto")
    usr_mock = DatosPersonalesUsuario(nombre="Juan", apellido="Perez")
    
    # Mock para la segunda query sin acoplarla al tipo exacto de JOIN usado.
    query_resenias.join.return_value = query_resenias
    query_resenias.outerjoin.return_value = query_resenias
    query_resenias.filter.return_value = query_resenias
    query_resenias.order_by.return_value = query_resenias
    query_resenias.all.return_value = [
        (val_mock, test_mock, usr_mock)
    ]
    
    resenias = obtener_resenias_vehiculo(db=db_mock, vehiculo_id=vehiculo_id)
    
    assert len(resenias) == 1
    assert resenias[0]["id_reserva"] == reserva_id
    assert resenias[0]["puntaje"] == 5
    assert resenias[0]["descripcion"] == "Excelente auto"
    assert resenias[0]["conductor"] == "Juan Perez"
    assert resenias[0]["fecha"] == fecha_val

def test_obtener_resenias_vacia():
    """
    Simula que el vehículo existe pero no tiene ninguna valoración/testimonio.
    Verifica que se devuelva una lista vacía.
    """
    db_mock = MagicMock()
    query_vehiculo = MagicMock()
    query_resenias = MagicMock()
    db_mock.query.side_effect = [query_vehiculo, query_resenias]
    vehiculo_id = uuid.uuid4()
    
    # Mock para la primera query (el auto existe)
    query_vehiculo.filter.return_value.first.return_value = Vehiculo(id=vehiculo_id)
    
    # Mock para la segunda query sin resultados.
    query_resenias.join.return_value = query_resenias
    query_resenias.outerjoin.return_value = query_resenias
    query_resenias.filter.return_value = query_resenias
    query_resenias.order_by.return_value = query_resenias
    query_resenias.all.return_value = []
    
    resenias = obtener_resenias_vehiculo(db=db_mock, vehiculo_id=vehiculo_id)
    
    assert len(resenias) == 0

def test_obtener_resenias_vehiculo_inexistente():
    """
    Simula que el vehículo consultado no existe en la DB.
    Verifica que levante la excepción de dominio correspondiente.
    """
    db_mock = MagicMock()
    vehiculo_id = uuid.uuid4()
    
    # Mock para devolver que no hay vehículo
    db_mock.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(VehiculoNoEncontradoError):
        obtener_resenias_vehiculo(db=db_mock, vehiculo_id=vehiculo_id)
