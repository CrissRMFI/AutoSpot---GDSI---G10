"""
Tests unitarios de la US 17D: Métricas de reputación y satisfacción.
"""
import uuid
from datetime import datetime
import pytest

from app.schemas.reputacion import MetricasReputacionSchema, ReseniaDetalleSchema
from app.models.valoracion import Valoracion
from app.models.testimonio import Testimonio
from app.models.datos_personales_usuario import DatosPersonalesUsuario

class MockQuery:
    def __init__(self, result):
        self.result = result

    def filter(self, *args, **kwargs):
        return self

    def outerjoin(self, *args, **kwargs):
        return self

    def join(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        return self.result


class MockDB:
    def __init__(self, queries):
        self.queries = queries
        self._query_idx = 0

    def query(self, *models):
        if self._query_idx < len(self.queries):
            result = self.queries[self._query_idx]
            self._query_idx += 1
            return MockQuery(result)
        return MockQuery([])


def test_calculo_metricas_reputacion_exitoso():
    """Test unitario: Cálculo correcto del promedio y listado de reseñas (Fase Roja)."""
    # IMPORTANTE: El servicio reputacion_service todavía no existe.
    from app.services.reputacion_service import obtener_metricas_reputacion_vehiculo

    vehiculo_id = uuid.uuid4()
    reserva1_id = uuid.uuid4()
    reserva2_id = uuid.uuid4()
    
    fecha1 = datetime(2023, 1, 1, 12, 0)
    fecha2 = datetime(2023, 1, 2, 12, 0)

    valoracion1 = Valoracion(id=uuid.uuid4(), reserva_id=reserva1_id, vehiculo_id=vehiculo_id, puntaje=5, created_at=fecha1)
    testimonio1 = Testimonio(id=uuid.uuid4(), reserva_id=reserva1_id, vehiculo_id=vehiculo_id, descripcion="Excelente auto", created_at=fecha1)
    
    valoracion2 = Valoracion(id=uuid.uuid4(), reserva_id=reserva2_id, vehiculo_id=vehiculo_id, puntaje=3, created_at=fecha2)
    # Simulamos una valoración sin testimonio asociado (o testimonio con descripcion None)
    testimonio2 = Testimonio(id=uuid.uuid4(), reserva_id=reserva2_id, vehiculo_id=vehiculo_id, descripcion=None, created_at=fecha2)

    datos1 = DatosPersonalesUsuario(nombre="Juan", apellido="Pérez")
    datos2 = DatosPersonalesUsuario(nombre="María", apellido="Gómez")

    db_mock = MockDB(queries=[
        [(valoracion1, testimonio1, datos1), (valoracion2, testimonio2, datos2)]
    ])

    resultado = obtener_metricas_reputacion_vehiculo(db=db_mock, vehiculo_id=vehiculo_id)

    assert isinstance(resultado, MetricasReputacionSchema)
    assert resultado.promedio_estrellas == 4.0
    assert resultado.cantidad_total == 2
    assert len(resultado.resenias) == 2
    
    assert resultado.resenias[0].puntaje == 5
    assert resultado.resenias[0].conductor == "Juan Pérez"
    assert resultado.resenias[0].comentario == "Excelente auto"
    assert resultado.resenias[0].fecha == fecha1
    
    assert resultado.resenias[1].puntaje == 3
    assert resultado.resenias[1].conductor == "María Gómez"
    assert resultado.resenias[1].comentario is None
    assert resultado.resenias[1].fecha == fecha2


def test_calculo_metricas_sin_resenias():
    """Test unitario: Comportamiento cuando un vehículo no tiene reseñas (Fase Roja)."""
    from app.services.reputacion_service import obtener_metricas_reputacion_vehiculo

    vehiculo_id = uuid.uuid4()
    db_mock = MockDB(queries=[[]])

    resultado = obtener_metricas_reputacion_vehiculo(db=db_mock, vehiculo_id=vehiculo_id)

    assert resultado.promedio_estrellas == 0.0
    assert resultado.cantidad_total == 0
    assert len(resultado.resenias) == 0
