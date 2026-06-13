from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.datos_personales_usuario import DatosPersonalesUsuarioSchema
from app.services.datos_personales_usuario import registrar_datos_personales
from app.services.vehiculo import obtener_historial_uso_vehiculo


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


def _registrar_datos_personales(db_session, usuario_id):
    registrar_datos_personales(
        db=db_session,
        usuario_id=usuario_id,
        schema=DatosPersonalesUsuarioSchema(
            dni="30111222",
            nombre="Lucia",
            apellido="Perez",
            foto_dni_frente_url="uploads/dni/30111222/frente.jpg",
            foto_dni_dorso_url="uploads/dni/30111222/dorso.jpg",
        ),
    )


def test_historial_muestra_fechas_pactadas_no_fechas_reales(db_session):
    propietario = _crear_usuario(
        db_session,
        "prop.historial.fechas@autospot.com",
        "PROPIETARIO",
    )
    conductor = _crear_usuario(db_session, "cliente.historial.fechas@autospot.com")
    _registrar_datos_personales(db_session, conductor.id)

    vehiculo = Vehiculo(
        propietario_id=propietario.id,
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        tipo_transmision="AUTOMATICA",
        capacidad=5,
        categoria="SEDAN",
        tipo_combustible="NAFTA",
        pets_friendly=True,
        patente="HH123II",
        estacion="Estación Belgrano",
        precio_por_dia=Decimal("48000.00"),
        estado_registro="HABILITADO",
        disponible=True,
    )
    db_session.add(vehiculo)
    db_session.commit()
    db_session.refresh(vehiculo)

    fecha_inicio_pactada = datetime(2026, 7, 15, 10, tzinfo=timezone.utc)
    fecha_fin_pactada = datetime(2026, 7, 17, 10, tzinfo=timezone.utc)
    fecha_salida_real = datetime.now(timezone.utc)
    fecha_devolucion_real = fecha_salida_real + timedelta(days=1)

    reserva = Reserva(
        vehiculo_id=vehiculo.id,
        conductor_id=conductor.id,
        codigo="AS-FECHAS",
        estado="FINALIZADA",
        monto_total=Decimal("96000.00"),
        fecha_inicio=fecha_inicio_pactada,
        fecha_fin=fecha_fin_pactada,
        fecha_salida_real=fecha_salida_real,
        fecha_devolucion_real=fecha_devolucion_real,
        estacion_retiro=vehiculo.estacion,
    )
    db_session.add(reserva)
    db_session.commit()

    historial = obtener_historial_uso_vehiculo(db=db_session, vehiculo_id=vehiculo.id)

    assert len(historial) == 1
    assert historial[0]["fecha_inicio"] == fecha_inicio_pactada
    assert historial[0]["fecha_fin"] == fecha_fin_pactada
