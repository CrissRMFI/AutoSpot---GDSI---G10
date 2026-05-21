"""
Tests Unitarios — Agregar fotos adicionales a un vehículo (lado EXTRA).

Cubre:
  - Aceptación del lado EXTRA en FotoVehiculoSchema.
  - Servicio agregar_foto_a_vehiculo:
      * happy path
      * vehículo inexistente
"""
import uuid

import pytest
from pydantic import ValidationError

from app.exceptions import VehiculoNoEncontradoError
from app.schemas.usuario import RegistroUsuarioSchema
from app.schemas.vehiculo import (
    FotoVehiculoSchema,
    RegistroVehiculoSchema,
)
from app.services.usuario import crear_usuario
from app.services.vehiculo import (
    agregar_foto_a_vehiculo,
    registrar_vehiculo,
)


def _payload_registro_vehiculo(propietario_id):
    return {
        "propietario_id": propietario_id,
        "marca": "Toyota",
        "modelo": "Corolla",
        "anio": 2020,
        "tipo_transmision": "AUTOMATICA",
        "capacidad": 5,
        "categoria": "SEDAN",
        "tipo_combustible": "NAFTA",
        "pets_friendly": True,
        "fotos": [
            {"lado": "FRENTE", "url": "u/frente.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
            {"lado": "TRASERA", "url": "u/trasera.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
            {"lado": "LATERAL_IZQUIERDO", "url": "u/li.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
            {"lado": "LATERAL_DERECHO", "url": "u/ld.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
            {"lado": "INTERIOR", "url": "u/interior.jpg", "formato": "jpg", "tamanio_bytes": 100_000},
        ],
    }


class TestSchemaLadoExtra:
    def test_lado_extra_es_valido(self):
        foto = FotoVehiculoSchema(
            lado="EXTRA",
            url="https://cdn.cloudinary.com/extra.jpg",
            formato="jpg",
            tamanio_bytes=500_000,
        )
        assert foto.lado == "EXTRA"

    def test_lado_invalido_sigue_rechazado(self):
        with pytest.raises(ValidationError) as exc_info:
            FotoVehiculoSchema(
                lado="DEBAJO",
                url="https://cdn.cloudinary.com/x.jpg",
                formato="jpg",
                tamanio_bytes=500_000,
            )
        mensajes = [e["msg"] for e in exc_info.value.errors()]
        assert any("Lado de foto invalido" in m for m in mensajes)


class TestAgregarFotoServicio:
    def test_agrega_foto_extra_a_vehiculo_existente(self, db_session):
        propietario = crear_usuario(
            db=db_session,
            schema=RegistroUsuarioSchema(
                email="agregar.foto@autospot.com",
                password="password123",
            ),
        )

        vehiculo = registrar_vehiculo(
            db=db_session,
            schema=RegistroVehiculoSchema(**_payload_registro_vehiculo(propietario.id)),
        )

        foto = agregar_foto_a_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            lado="EXTRA",
            url="https://cdn.cloudinary.com/extra-1.jpg",
            formato="jpg",
            tamanio_bytes=200_000,
        )

        assert foto.id is not None
        assert foto.vehiculo_id == vehiculo.id
        assert foto.lado == "EXTRA"
        assert foto.url == "https://cdn.cloudinary.com/extra-1.jpg"

        db_session.refresh(vehiculo)
        assert len(vehiculo.fotos) == 6

    def test_lanza_excepcion_si_vehiculo_no_existe(self, db_session):
        with pytest.raises(VehiculoNoEncontradoError):
            agregar_foto_a_vehiculo(
                db=db_session,
                vehiculo_id=uuid.uuid4(),
                lado="EXTRA",
                url="https://cdn.cloudinary.com/x.jpg",
                formato="jpg",
                tamanio_bytes=100_000,
            )
