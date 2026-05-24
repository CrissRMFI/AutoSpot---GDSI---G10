"""
Tests Unitarios — US 3R: Abrir documentación.

La US 3R permite al ADMIN abrir una solicitud de la cola para ver el detalle
documental completo antes de aprobar o rechazar en historias posteriores.
"""
import uuid
from datetime import date, datetime, timezone

import pytest

from app.exceptions import (
    SolicitudDocumentacionNoEncontradaError,
    TipoSolicitudDocumentacionInvalidoError,
)
from app.models.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductor,
)
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.solicitud_documentacion import (
    TIPO_SOLICITUD_CONDUCTOR,
    TIPO_SOLICITUD_VEHICULO,
)
from app.services.solicitud_documentacion import (
    obtener_detalle_solicitud_documentacion,
)


def _crear_usuario(db_session, email: str, rol: str = "CLIENTE") -> Usuario:
    usuario = Usuario(email=email, hashed_password="x" * 60, rol=rol)
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


def _crear_vehiculo_documentado(db_session, propietario_id) -> Vehiculo:
    ahora = datetime.now(timezone.utc)
    vehiculo = Vehiculo(
        propietario_id=propietario_id,
        marca="Toyota",
        modelo="Corolla",
        anio=2023,
        tipo_transmision="AUTOMATICA",
        capacidad=5,
        categoria="SEDAN",
        tipo_combustible="NAFTA",
        pets_friendly=True,
        patente="AB123CD",
        chasis="CHASIS-123",
        motor="MOTOR-123",
        titular="Roberto Garcia",
        cedula="https://cdn.autospot.test/cedula.jpg",
        poliza="https://cdn.autospot.test/poliza.jpg",
        vtv="https://cdn.autospot.test/vtv.jpg",
        estacion="Palermo",
        telefono="+541100000000",
        descripcion="Documentacion legal completa.",
        estado_registro="EN_REVISION",
        created_at=ahora,
        updated_at=ahora,
    )
    db_session.add(vehiculo)
    db_session.commit()
    db_session.refresh(vehiculo)
    return vehiculo


def _crear_documentacion_conductor(db_session, usuario_id):
    ahora = datetime.now(timezone.utc)
    documentacion = DocumentacionHabilitanteConductor(
        usuario_id=usuario_id,
        numero_licencia="LIC-3R-001",
        categoria="B",
        fecha_emision=date(2024, 1, 1),
        fecha_vencimiento=date(2029, 1, 1),
        foto_licencia_frente_url="https://cdn.autospot.test/lic-frente.jpg",
        foto_licencia_dorso_url="https://cdn.autospot.test/lic-dorso.jpg",
        estado_validacion="PENDIENTE_REVISION",
        created_at=ahora,
        updated_at=ahora,
    )
    db_session.add(documentacion)
    db_session.commit()
    db_session.refresh(documentacion)
    return documentacion


class TestUS3RServicioAbrirDocumentacion:
    def test_abre_detalle_de_documentacion_de_vehiculo(self, db_session):
        propietario = _crear_usuario(
            db_session,
            "propietario.us3r@autospot.com",
            rol="PROPIETARIO",
        )
        vehiculo = _crear_vehiculo_documentado(db_session, propietario.id)

        detalle = obtener_detalle_solicitud_documentacion(
            db=db_session,
            tipo=TIPO_SOLICITUD_VEHICULO,
            recurso_id=vehiculo.id,
        )

        assert detalle.tipo == TIPO_SOLICITUD_VEHICULO
        assert detalle.recurso_id == vehiculo.id
        assert detalle.usuario_email == "propietario.us3r@autospot.com"
        assert detalle.patente == "AB123CD"
        assert detalle.chasis == "CHASIS-123"
        assert detalle.motor == "MOTOR-123"
        assert detalle.titular == "Roberto Garcia"
        assert [documento.nombre for documento in detalle.documentos] == [
            "Cedula verde / titulo",
            "Poliza de seguro",
            "VTV / revision tecnica",
        ]

    def test_abre_detalle_de_documentacion_de_conductor(self, db_session):
        conductor = _crear_usuario(db_session, "conductor.us3r@autospot.com")
        documentacion = _crear_documentacion_conductor(db_session, conductor.id)

        detalle = obtener_detalle_solicitud_documentacion(
            db=db_session,
            tipo=TIPO_SOLICITUD_CONDUCTOR,
            recurso_id=documentacion.id,
        )

        assert detalle.tipo == TIPO_SOLICITUD_CONDUCTOR
        assert detalle.recurso_id == documentacion.id
        assert detalle.usuario_email == "conductor.us3r@autospot.com"
        assert detalle.numero_licencia == "LIC-3R-001"
        assert detalle.categoria_licencia == "B"
        assert [documento.nombre for documento in detalle.documentos] == [
            "Licencia frente",
            "Licencia dorso",
        ]

    def test_tipo_invalido_falla(self, db_session):
        with pytest.raises(TipoSolicitudDocumentacionInvalidoError):
            obtener_detalle_solicitud_documentacion(
                db=db_session,
                tipo="OTRO",
                recurso_id=uuid.uuid4(),
            )

    def test_recurso_inexistente_falla(self, db_session):
        with pytest.raises(SolicitudDocumentacionNoEncontradaError):
            obtener_detalle_solicitud_documentacion(
                db=db_session,
                tipo=TIPO_SOLICITUD_VEHICULO,
                recurso_id=uuid.uuid4(),
            )
