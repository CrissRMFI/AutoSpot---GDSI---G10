import pytest
import uuid
# pyrefly: ignore [missing-import]
from pydantic import ValidationError

from app.exceptions import (
    DocumentacionVehiculoNoEditableError,
    UsuarioNoEncontradoError,
    VehiculoNoEncontradoError,
    VehiculoNoHabilitadoError,
    VehiculoConReservaActivaError,
)
from app.schemas.usuario import RegistroUsuarioSchema
from app.schemas.vehiculo import (
    RegistroVehiculoSchema,
    FotoVehiculoSchema,
    ActualizarVehiculoPayloadSchema,
)
from app.services.usuario import crear_usuario
from app.services.vehiculo import (
    registrar_vehiculo,
    actualizar_vehiculo,
    cambiar_disponibilidad_vehiculo,
    obtener_vehiculo,
)

class TestActualizarVehiculoService:
    """
    Tests para el servicio de actualización de vehículos y disponibilidad.
    """

    @pytest.fixture
    def usuario_y_vehiculo(self, db_session):
        propietario = crear_usuario(
            db=db_session,
            schema=RegistroUsuarioSchema(
                email="propietario@autospot.com",
                password="password123",
            ),
        )

        payload_registro = RegistroVehiculoSchema(
            propietario_id=propietario.id,
            marca="Toyota",
            modelo="Corolla",
            anio=2020,
            tipo_transmision="AUTOMATICA",
            capacidad=5,
            categoria="SEDAN",
            tipo_combustible="NAFTA",
            pets_friendly=True,
            fotos=[
                FotoVehiculoSchema(
                    lado="FRENTE",
                    url="frente.jpg",
                    formato="jpg",
                    tamanio_bytes=500,
                ),
                FotoVehiculoSchema(
                    lado="TRASERA",
                    url="trasera.jpg",
                    formato="jpg",
                    tamanio_bytes=500,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_IZQUIERDO",
                    url="izq.jpg",
                    formato="jpg",
                    tamanio_bytes=500,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_DERECHO",
                    url="der.jpg",
                    formato="jpg",
                    tamanio_bytes=500,
                ),
                FotoVehiculoSchema(
                    lado="INTERIOR",
                    url="interior.jpg",
                    formato="jpg",
                    tamanio_bytes=500,
                ),
            ],
        )
        vehiculo = registrar_vehiculo(db=db_session, schema=payload_registro)
        return propietario, vehiculo

    def test_actualizar_vehiculo_modifica_datos_y_fotos(self, db_session, usuario_y_vehiculo):
        propietario, vehiculo = usuario_y_vehiculo

        payload_actualizacion = ActualizarVehiculoPayloadSchema(
            marca="Toyota",  # Esto debe ser ignorado
            modelo="Corolla", # Esto debe ser ignorado
            anio=2022,
            tipo_transmision="MANUAL",
            capacidad=4,
            categoria="HATCHBACK",
            tipo_combustible="GNC",
            pets_friendly=False,
            fotos=[
                FotoVehiculoSchema(
                    lado="FRENTE",
                    url="nuevo_frente.jpg",
                    formato="jpg",
                    tamanio_bytes=600,
                ),
                FotoVehiculoSchema(
                    lado="TRASERA",
                    url="nuevo_trasera.jpg",
                    formato="jpg",
                    tamanio_bytes=600,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_IZQUIERDO",
                    url="nuevo_izq.jpg",
                    formato="jpg",
                    tamanio_bytes=600,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_DERECHO",
                    url="nuevo_der.jpg",
                    formato="jpg",
                    tamanio_bytes=600,
                ),
                FotoVehiculoSchema(
                    lado="INTERIOR",
                    url="nuevo_interior.jpg",
                    formato="jpg",
                    tamanio_bytes=600,
                ),
            ],
        )

        vehiculo_actualizado = actualizar_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            schema=payload_actualizacion
        )

        # Verificar que marca y modelo no se actualizaron
        assert vehiculo_actualizado.marca == "Toyota"
        assert vehiculo_actualizado.modelo == "Corolla"

        # Verificar que el resto de las propiedades sí se actualizaron
        assert vehiculo_actualizado.anio == 2022
        assert vehiculo_actualizado.tipo_transmision == "MANUAL"
        assert vehiculo_actualizado.capacidad == 4
        assert vehiculo_actualizado.categoria == "HATCHBACK"
        assert vehiculo_actualizado.tipo_combustible == "GNC"
        assert vehiculo_actualizado.pets_friendly is False

        # Verificar que se reemplazaron las fotos
        assert len(vehiculo_actualizado.fotos) == 5
        url_fotos = [f.url for f in vehiculo_actualizado.fotos]
        assert "nuevo_frente.jpg" in url_fotos

    def test_actualizar_datos_documentales_rechazado_es_valido(
        self,
        db_session,
        usuario_y_vehiculo,
    ):
        _, vehiculo = usuario_y_vehiculo
        vehiculo.estado_registro = "RECHAZADO"
        db_session.commit()

        payload_actualizacion = ActualizarVehiculoPayloadSchema(
            marca="Toyota",
            modelo="Corolla",
            anio=2020,
            tipo_transmision="AUTOMATICA",
            capacidad=5,
            categoria="SEDAN",
            tipo_combustible="NAFTA",
            pets_friendly=True,
            patente="AB123CD",
            chasis="CHASIS123",
            motor="MOTOR123",
            titular="Juan Propietario",
            estacion="Palermo",
            telefono="1122334455",
            fotos=[
                FotoVehiculoSchema(lado="FRENTE", url="f.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="TRASERA", url="t.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="LATERAL_IZQUIERDO", url="i.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="LATERAL_DERECHO", url="d.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="INTERIOR", url="int.jpg", formato="jpg", tamanio_bytes=100),
            ],
        )

        vehiculo_actualizado = actualizar_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            schema=payload_actualizacion,
        )

        assert vehiculo_actualizado.patente == "AB123CD"
        assert vehiculo_actualizado.chasis == "CHASIS123"
        assert vehiculo_actualizado.motor == "MOTOR123"

    def test_actualizar_datos_documentales_habilitado_lanza_error(
        self,
        db_session,
        usuario_y_vehiculo,
    ):
        _, vehiculo = usuario_y_vehiculo
        vehiculo.estado_registro = "HABILITADO"
        vehiculo.patente = "AA111AA"
        db_session.commit()

        payload_actualizacion = ActualizarVehiculoPayloadSchema(
            marca="Toyota",
            modelo="Corolla",
            anio=2020,
            tipo_transmision="AUTOMATICA",
            capacidad=5,
            categoria="SEDAN",
            tipo_combustible="NAFTA",
            pets_friendly=True,
            patente="BB222BB",
            fotos=[
                FotoVehiculoSchema(lado="FRENTE", url="f.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="TRASERA", url="t.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="LATERAL_IZQUIERDO", url="i.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="LATERAL_DERECHO", url="d.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="INTERIOR", url="int.jpg", formato="jpg", tamanio_bytes=100),
            ],
        )

        with pytest.raises(DocumentacionVehiculoNoEditableError):
            actualizar_vehiculo(
                db=db_session,
                vehiculo_id=vehiculo.id,
                schema=payload_actualizacion,
            )

    def test_actualizar_vehiculo_inexistente_lanza_error(self, db_session):
        payload_actualizacion = ActualizarVehiculoPayloadSchema(
            marca="Toyota",
            modelo="Corolla",
            anio=2022,
            tipo_transmision="MANUAL",
            capacidad=4,
            categoria="SEDAN",
            tipo_combustible="GNC",
            pets_friendly=False,
            fotos=[
                FotoVehiculoSchema(lado="FRENTE", url="f.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="TRASERA", url="t.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="LATERAL_IZQUIERDO", url="i.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="LATERAL_DERECHO", url="d.jpg", formato="jpg", tamanio_bytes=100),
                FotoVehiculoSchema(lado="INTERIOR", url="int.jpg", formato="jpg", tamanio_bytes=100),
            ],
        )

        with pytest.raises(VehiculoNoEncontradoError):
            actualizar_vehiculo(
                db=db_session,
                vehiculo_id=uuid.uuid4(),
                schema=payload_actualizacion
            )

    def test_obtener_vehiculo_exitoso(self, db_session, usuario_y_vehiculo):
        _, vehiculo = usuario_y_vehiculo
        vehiculo_obtenido = obtener_vehiculo(db=db_session, vehiculo_id=vehiculo.id)
        assert vehiculo_obtenido.id == vehiculo.id

    def test_obtener_vehiculo_inexistente_lanza_error(self, db_session):
        with pytest.raises(VehiculoNoEncontradoError):
            obtener_vehiculo(db=db_session, vehiculo_id=uuid.uuid4())

    def test_cambiar_disponibilidad_vehiculo_no_habilitado_lanza_error(self, db_session, usuario_y_vehiculo):
        _, vehiculo = usuario_y_vehiculo
        # Por defecto el vehículo está en PENDIENTE_DOCUMENTACION
        with pytest.raises(VehiculoNoHabilitadoError):
            cambiar_disponibilidad_vehiculo(
                db=db_session,
                vehiculo_id=vehiculo.id,
                disponible=True
            )

    def test_cambiar_disponibilidad_vehiculo_exitoso(self, db_session, usuario_y_vehiculo):
        _, vehiculo = usuario_y_vehiculo
        
        # Simular que el vehículo fue habilitado
        vehiculo.estado_registro = "HABILITADO"
        db_session.commit()

        vehiculo_actualizado = cambiar_disponibilidad_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            disponible=True
        )

        assert vehiculo_actualizado.disponible is True

    def test_cambiar_disponibilidad_vehiculo_inexistente_lanza_error(self, db_session):
        with pytest.raises(VehiculoNoEncontradoError):
            cambiar_disponibilidad_vehiculo(
                db=db_session,
                vehiculo_id=uuid.uuid4(),
                disponible=True
            )
