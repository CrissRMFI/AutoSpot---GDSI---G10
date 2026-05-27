import pytest
from unittest.mock import MagicMock
from app.services.solicitud_documentacion import resolver_solicitud
from app.exceptions import TipoSolicitudDocumentacionInvalidoError, SolicitudDocumentacionNoEncontradaError
from app.models.documentacion_habilitante_conductor import EstadoHabilitacion

def test_aprobar_vehiculo_cambia_estado_a_habilitado():
    db_mock = MagicMock()
    vehiculo_mock = MagicMock()
    db_mock.query().filter().first.return_value = vehiculo_mock
    
    resolver_solicitud(db_mock, "VEHICULO", "some-uuid", aprobada=True)
    
    assert vehiculo_mock.estado_registro == "HABILITADO"
    assert vehiculo_mock.motivo_rechazo is None
    db_mock.commit.assert_called_once()

def test_rechazar_vehiculo_guarda_motivo_y_cambia_estado():
    db_mock = MagicMock()
    vehiculo_mock = MagicMock()
    db_mock.query().filter().first.return_value = vehiculo_mock
    
    resolver_solicitud(db_mock, "VEHICULO", "some-uuid", aprobada=False, motivo_rechazo="Documentos ilegibles")
    
    assert vehiculo_mock.estado_registro == "RECHAZADO"
    assert vehiculo_mock.motivo_rechazo == "Documentos ilegibles"
    db_mock.commit.assert_called_once()

def test_rechazar_sin_motivo_lanza_excepcion():
    db_mock = MagicMock()
    
    with pytest.raises(ValueError, match="El motivo de rechazo es obligatorio para rechazar la solicitud"):
        resolver_solicitud(db_mock, "VEHICULO", "some-uuid", aprobada=False, motivo_rechazo="   ")

def test_aprobar_conductor_cambia_estado_a_aprobado():
    db_mock = MagicMock()
    conductor_mock = MagicMock()
    db_mock.query().filter().first.return_value = conductor_mock
    
    resolver_solicitud(db_mock, "CONDUCTOR", "some-uuid", aprobada=True)
    
    assert conductor_mock.estado_validacion == EstadoHabilitacion.APROBADO
    assert conductor_mock.motivo_rechazo is None
    db_mock.commit.assert_called_once()

def test_rechazar_conductor_guarda_motivo_y_cambia_estado():
    db_mock = MagicMock()
    conductor_mock = MagicMock()
    db_mock.query().filter().first.return_value = conductor_mock
    
    resolver_solicitud(db_mock, "CONDUCTOR", "some-uuid", aprobada=False, motivo_rechazo="Licencia vencida")
    
    assert conductor_mock.estado_validacion == EstadoHabilitacion.RECHAZADO
    assert conductor_mock.motivo_rechazo == "Licencia vencida"
    db_mock.commit.assert_called_once()
