import uuid
import pytest
from unittest.mock import MagicMock

from app.services.solicitud_documentacion import (
    aprobar_solicitud_documentacion,
    rechazar_solicitud_documentacion,
)
from app.models.vehiculo import Vehiculo
from app.models.documentacion_habilitante_conductor import DocumentacionHabilitanteConductor, EstadoHabilitacion
from app.exceptions import (
    SolicitudDocumentacionNoEncontradaError,
    TipoSolicitudDocumentacionInvalidoError,
    MotivoRechazoVacioError,
)
from app.schemas.solicitud_documentacion import TIPO_SOLICITUD_VEHICULO, TIPO_SOLICITUD_CONDUCTOR


class TestUS4RValidarDocumentacionLogica:
    """
    Pruebas unitarias aisladas para la lógica de validación de documentación (US 4R).
    Utiliza Mocks para simular la base de datos sin levantar el entorno completo ni HTTP.
    """

    def test_aprobar_solicitud_vehiculo_cambia_estado(self):
        db_mock = MagicMock()
        vehiculo_mock = Vehiculo(id=uuid.uuid4(), estado_registro="EN_REVISION")
        # Simular que db.query().filter().first() devuelve el vehiculo_mock
        db_mock.query().filter().first.return_value = vehiculo_mock
        
        aprobar_solicitud_documentacion(db_mock, TIPO_SOLICITUD_VEHICULO, vehiculo_mock.id)
        
        assert vehiculo_mock.estado_registro == "VALIDADO"
        assert vehiculo_mock.motivo_rechazo is None
        db_mock.commit.assert_called_once()

    def test_aprobar_solicitud_conductor_cambia_estado(self):
        db_mock = MagicMock()
        doc_mock = DocumentacionHabilitanteConductor(
            id=uuid.uuid4(), 
            estado_validacion=EstadoHabilitacion.PENDIENTE_REVISION
        )
        db_mock.query().filter().first.return_value = doc_mock
        
        aprobar_solicitud_documentacion(db_mock, TIPO_SOLICITUD_CONDUCTOR, doc_mock.id)
        
        assert doc_mock.estado_validacion == EstadoHabilitacion.APROBADO
        assert doc_mock.motivo_rechazo is None
        db_mock.commit.assert_called_once()

    def test_rechazar_solicitud_vehiculo_cambia_estado(self):
        db_mock = MagicMock()
        vehiculo_mock = Vehiculo(id=uuid.uuid4(), estado_registro="EN_REVISION")
        db_mock.query().filter().first.return_value = vehiculo_mock
        
        motivo = "No se ve clara la cedula"
        rechazar_solicitud_documentacion(db_mock, TIPO_SOLICITUD_VEHICULO, vehiculo_mock.id, motivo)
        
        assert vehiculo_mock.estado_registro == "RECHAZADO"
        assert vehiculo_mock.motivo_rechazo == motivo
        db_mock.commit.assert_called_once()

    def test_rechazar_solicitud_conductor_cambia_estado(self):
        db_mock = MagicMock()
        doc_mock = DocumentacionHabilitanteConductor(
            id=uuid.uuid4(), 
            estado_validacion=EstadoHabilitacion.PENDIENTE_REVISION
        )
        db_mock.query().filter().first.return_value = doc_mock
        
        motivo = "Licencia vencida"
        rechazar_solicitud_documentacion(db_mock, TIPO_SOLICITUD_CONDUCTOR, doc_mock.id, motivo)
        
        assert doc_mock.estado_validacion == EstadoHabilitacion.RECHAZADO
        assert doc_mock.motivo_rechazo == motivo
        db_mock.commit.assert_called_once()

    def test_rechazar_con_motivo_vacio_lanza_error(self):
        db_mock = MagicMock()
        
        with pytest.raises(MotivoRechazoVacioError) as exc_info:
            rechazar_solicitud_documentacion(db_mock, TIPO_SOLICITUD_VEHICULO, uuid.uuid4(), "")
        
        assert str(exc_info.value) == "El motivo de rechazo es obligatorio"
        db_mock.commit.assert_not_called()

        with pytest.raises(MotivoRechazoVacioError):
            rechazar_solicitud_documentacion(db_mock, TIPO_SOLICITUD_VEHICULO, uuid.uuid4(), "   ")

    def test_aprobar_tipo_invalido_lanza_error(self):
        db_mock = MagicMock()
        with pytest.raises(TipoSolicitudDocumentacionInvalidoError):
            aprobar_solicitud_documentacion(db_mock, "OTRO_TIPO", uuid.uuid4())

    def test_rechazar_tipo_invalido_lanza_error(self):
        db_mock = MagicMock()
        with pytest.raises(TipoSolicitudDocumentacionInvalidoError):
            rechazar_solicitud_documentacion(db_mock, "OTRO_TIPO", uuid.uuid4(), "Motivo de prueba")

    def test_aprobar_recurso_no_encontrado_lanza_error(self):
        db_mock = MagicMock()
        db_mock.query().filter().first.return_value = None
        
        with pytest.raises(SolicitudDocumentacionNoEncontradaError):
            aprobar_solicitud_documentacion(db_mock, TIPO_SOLICITUD_VEHICULO, uuid.uuid4())

    def test_rechazar_recurso_no_encontrado_lanza_error(self):
        db_mock = MagicMock()
        db_mock.query().filter().first.return_value = None
        
        with pytest.raises(SolicitudDocumentacionNoEncontradaError):
            rechazar_solicitud_documentacion(db_mock, TIPO_SOLICITUD_CONDUCTOR, uuid.uuid4(), "Motivo")
