"""
Pruebas Unitarias — US 10R: Historial de autos.
"""
import uuid
from datetime import date
from unittest.mock import MagicMock

from app.services.historial_autos import obtener_historial_autos


def test_obtener_historial_autos_vacio():
    """Valida que si no hay reservas, devuelve una lista vacía."""
    db_mock = MagicMock()
    q_mock = MagicMock()
    db_mock.query.return_value = q_mock
    q_mock.join.return_value = q_mock
    q_mock.outerjoin.return_value = q_mock
    q_mock.filter.return_value = q_mock
    q_mock.order_by.return_value = q_mock
    q_mock.all.return_value = []

    resultado = obtener_historial_autos(db_mock)
    assert resultado == []


def test_obtener_historial_autos_filtros():
    """Valida que la función procese correctamente los parámetros de filtrado."""
    db_mock = MagicMock()
    q_mock = MagicMock()
    db_mock.query.return_value = q_mock
    q_mock.join.return_value = q_mock
    q_mock.outerjoin.return_value = q_mock
    q_mock.filter.return_value = q_mock
    q_mock.order_by.return_value = q_mock
    q_mock.all.return_value = []

    obtener_historial_autos(
        db_mock,
        estacion="Obelisco",
        fecha=date(2026, 6, 16),
        patente="AB123"
    )

    # Debería haber llamado a filter varias veces por los parámetros provistos
    assert q_mock.filter.call_count >= 3
