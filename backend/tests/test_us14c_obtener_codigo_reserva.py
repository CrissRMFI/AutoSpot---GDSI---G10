"""
Tests Unitarios — US 14C: Obtener código de reserva.
"""
from decimal import Decimal
from datetime import datetime, timedelta, timezone

from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.alquiler import CrearReservaPayloadSchema
from app.services.alquiler_service import crear_reserva_con_codigo
from app.schemas.datos_personales_usuario import DatosPersonalesUsuarioSchema
from app.services.datos_personales_usuario import registrar_datos_personales


def _crear_usuario(db_session, email: str, rol: str = "CLIENTE") -> Usuario:
    usuario = Usuario(
        email=email,
        hashed_password="hash",
        rol=rol,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario

def _registrar_datos_personales(db_session, usuario_id: str):
        payload = DatosPersonalesUsuarioSchema(
            dni="12345678",
            nombre="Mateo",
            apellido="Gomez",
            foto_dni_frente_url="uploads/dni/12345678/frente.jpg",
            foto_dni_dorso_url="uploads/dni/12345678/dorso.jpg",
        )

        registrar_datos_personales(
            db=db_session,
            usuario_id=usuario_id,
            schema=payload,
        )

def _crear_vehiculo_reservable(db_session, propietario_id) -> Vehiculo:
    vehiculo = Vehiculo(
        propietario_id=propietario_id,
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        tipo_transmision="AUTOMATICA",
        capacidad=5,
        categoria="SEDAN",
        tipo_combustible="NAFTA",
        pets_friendly=True,
        kilometros=50000,
        patente="AB123CD",
        estacion="Estación Belgrano",
        precio_por_dia=Decimal("48000.00"),
        estado_registro="HABILITADO",
        disponible=True,
    )
    db_session.add(vehiculo)
    db_session.commit()
    db_session.refresh(vehiculo)
    return vehiculo


def test_crea_reserva_confirmada_con_codigo(db_session):
    propietario = _crear_usuario(db_session, "prop.us14c@autospot.com", "PROPIETARIO")
    conductor = _crear_usuario(db_session, "cliente.us14c@autospot.com")
    _registrar_datos_personales(db_session, conductor.id)
    vehiculo = _crear_vehiculo_reservable(db_session, propietario.id)
    antes_de_crear = datetime.now(timezone.utc)
    fin = antes_de_crear + timedelta(days=2, hours=12)

    reserva = crear_reserva_con_codigo(
        db=db_session,
        conductor_id=conductor.id,
        schema=CrearReservaPayloadSchema(
            vehiculo_id=vehiculo.id,
            fecha_fin=fin,
        ),
    )
    despues_de_crear = datetime.now(timezone.utc)

    db_session.refresh(vehiculo)
    assert reserva.estado == "CONFIRMADA"
    assert reserva.codigo.startswith("AS-")
    assert reserva.codigo_verificado_at is None
    assert reserva.estacion_retiro == "Estación Belgrano"
    assert reserva.monto_total > Decimal("0")
    assert antes_de_crear <= reserva.fecha_inicio <= despues_de_crear
    assert reserva.fecha_fin == fin
    assert vehiculo.disponible is False
