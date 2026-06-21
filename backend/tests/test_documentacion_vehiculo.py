"""
Tests Unitarios — Cargar documentación legal del vehículo.

Este flujo es posterior al alta inicial del vehículo. El vehículo ya existe
con características y fotos, y luego se cargan los datos documentales.
"""
import uuid

import pytest
from pydantic import ValidationError

from app.exceptions import (
    DocumentacionVehiculoNoEditableError,
    VehiculoNoEncontradoError,
)
from app.schemas.usuario import RegistroUsuarioSchema
from app.schemas.vehiculo import (
    DocumentacionVehiculoSchema,
    FotoVehiculoSchema,
    RegistroVehiculoSchema,
)
from app.services.usuario import crear_usuario
from app.services.vehiculo import (
    cargar_documentacion_vehiculo,
    registrar_vehiculo,
)


def crear_vehiculo_base(db_session):
    """
    Helper para crear un vehículo válido en estado PENDIENTE_DOCUMENTACION.
    """
    propietario = crear_usuario(
        db=db_session,
        schema=RegistroUsuarioSchema(
            email="propietario.documentacion@autospot.com",
            password="password123",
        ),
    )

    vehiculo = registrar_vehiculo(
        db=db_session,
        schema=RegistroVehiculoSchema(
            propietario_id=propietario.id,
            marca="Toyota",
            modelo="Corolla",
            anio=2020,
            tipo_transmision="AUTOMATICA",
            capacidad=5,
            categoria="SEDAN",
            tipo_combustible="NAFTA",
            pets_friendly=True,
            kilometros=50000,
            fotos=[
                FotoVehiculoSchema(
                    lado="FRENTE",
                    url="uploads/vehiculos/corolla/frente.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="TRASERA",
                    url="uploads/vehiculos/corolla/trasera.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_IZQUIERDO",
                    url="uploads/vehiculos/corolla/lateral_izquierdo.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_DERECHO",
                    url="uploads/vehiculos/corolla/lateral_derecho.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="INTERIOR",
                    url="uploads/vehiculos/corolla/interior.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
            ],
        ),
    )

    return vehiculo


def payload_documentacion_valido() -> DocumentacionVehiculoSchema:
    """
    Helper para construir un payload documental válido.
    """
    return DocumentacionVehiculoSchema(
        patente="ABC123",
        chasis="CHASIS123",
        motor="MOTOR123",
        titular="Juan Propietario",
        cedula="cedula.pdf",
        poliza="poliza.pdf",
        vtv="vtv.pdf",
        estacion="Palermo",
        telefono="1122334455",
        descripcion="Documentación cargada para revisión.",
    )


class TestCargaDocumentacionVehiculo:
    """
    Verifica la carga exitosa de documentación legal sobre un vehículo existente.
    """

    def test_carga_documentacion_legal_en_vehiculo_existente(self, db_session):
        vehiculo = crear_vehiculo_base(db_session)
        schema = payload_documentacion_valido()

        vehiculo_actualizado = cargar_documentacion_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            schema=schema,
        )

        assert vehiculo_actualizado.id == vehiculo.id
        assert vehiculo_actualizado.patente == "ABC123"
        assert vehiculo_actualizado.chasis == "CHASIS123"
        assert vehiculo_actualizado.motor == "MOTOR123"
        assert vehiculo_actualizado.titular == "Juan Propietario"
        assert vehiculo_actualizado.cedula == "cedula.pdf"
        assert vehiculo_actualizado.poliza == "poliza.pdf"
        assert vehiculo_actualizado.vtv == "vtv.pdf"
        assert vehiculo_actualizado.estacion == "Palermo"
        assert vehiculo_actualizado.telefono == "1122334455"
        assert (
            vehiculo_actualizado.descripcion
            == "Documentación cargada para revisión."
        )

        assert vehiculo_actualizado.estado_registro == "EN_REVISION"


class TestErroresDocumentacionVehiculo:
    """
    Verifica errores de negocio y validación del flujo documental.
    """

    def test_no_carga_documentacion_si_vehiculo_no_existe(self, db_session):
        schema = payload_documentacion_valido()

        with pytest.raises(VehiculoNoEncontradoError):
            cargar_documentacion_vehiculo(
                db=db_session,
                vehiculo_id=uuid.uuid4(),
                schema=schema,
            )

    def test_no_carga_documentacion_si_vehiculo_habilitado(self, db_session):
        vehiculo = crear_vehiculo_base(db_session)
        vehiculo.estado_registro = "HABILITADO"
        db_session.commit()
        schema = payload_documentacion_valido()

        with pytest.raises(DocumentacionVehiculoNoEditableError):
            cargar_documentacion_vehiculo(
                db=db_session,
                vehiculo_id=vehiculo.id,
                schema=schema,
            )

    def test_carga_documentacion_si_vehiculo_rechazado(self, db_session):
        vehiculo = crear_vehiculo_base(db_session)
        vehiculo.estado_registro = "RECHAZADO"
        vehiculo.motivo_rechazo = "Documento ilegible"
        db_session.commit()
        schema = payload_documentacion_valido()

        vehiculo_actualizado = cargar_documentacion_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            schema=schema,
        )

        assert vehiculo_actualizado.estado_registro == "EN_REVISION"
        assert vehiculo_actualizado.motivo_rechazo is None

    @pytest.mark.parametrize(
        "campo",
        [
            "patente",
            "chasis",
            "motor",
            "titular",
            "cedula",
            "poliza",
            "vtv",
            "estacion",
            "telefono",
        ],
    )
    def test_campo_obligatorio_vacio_es_invalido(self, campo):
        payload = {
            "patente": "ABC123",
            "chasis": "CHASIS123",
            "motor": "MOTOR123",
            "titular": "Juan Propietario",
            "cedula": "cedula.pdf",
            "poliza": "poliza.pdf",
            "vtv": "vtv.pdf",
            "estacion": "Palermo",
            "telefono": "1122334455",
            "descripcion": "Documentación cargada.",
        }
        payload[campo] = ""

        with pytest.raises(ValidationError) as exc_info:
            DocumentacionVehiculoSchema(**payload)

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any("Campo obligatorio" in mensaje for mensaje in mensajes)

    def test_descripcion_vacia_se_normaliza_a_none(self):
        schema = DocumentacionVehiculoSchema(
            patente="ABC123",
            chasis="CHASIS123",
            motor="MOTOR123",
            titular="Juan Propietario",
            cedula="cedula.pdf",
            poliza="poliza.pdf",
            vtv="vtv.pdf",
            estacion="Palermo",
            telefono="1122334455",
            descripcion="   ",
        )

        assert schema.descripcion is None
