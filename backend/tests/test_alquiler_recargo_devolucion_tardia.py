from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.services.alquiler_service import entregar_auto, motivo_bloqueo_entrega
from app.services.reglas_financieras import calcular_recargo_devolucion_tardia


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


def _crear_vehiculo(db_session, propietario_id) -> Vehiculo:
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
        patente="SI123NO",
        estacion="Estación Belgrano",
        precio_por_dia=Decimal("50000.00"),
        estado_registro="HABILITADO",
        disponible=False,
    )
    db_session.add(vehiculo)
    db_session.commit()
    db_session.refresh(vehiculo)
    return vehiculo


def test_inicio_pasado_no_bloquea_entrega_admin(db_session):
    propietario = _crear_usuario(db_session, "prop.entrega.sin-bloqueo@autospot.com", "PROPIETARIO")
    conductor = _crear_usuario(db_session, "cliente.entrega.sin-bloqueo@autospot.com")
    vehiculo = _crear_vehiculo(db_session, propietario.id)

    reserva = Reserva(
        vehiculo_id=vehiculo.id,
        conductor_id=conductor.id,
        codigo="AS-NOBLOCK",
        estado="CONFIRMADA",
        monto_total=Decimal("50000.00"),
        fecha_inicio=datetime.now(timezone.utc) - timedelta(hours=3),
        fecha_fin=datetime.now(timezone.utc) + timedelta(days=1),
        estacion_retiro=vehiculo.estacion,
    )

    assert motivo_bloqueo_entrega(reserva) is None


def test_regla_financiera_calcula_recargo_por_dias_de_retraso():
    fecha_estimada = datetime(2026, 7, 10, 10, tzinfo=timezone.utc)
    fecha_real = fecha_estimada + timedelta(days=1, minutes=1)

    minutos, dias, monto = calcular_recargo_devolucion_tardia(
        precio_por_dia=Decimal("50000.00"),
        fecha_entrega_estimada=fecha_estimada,
        fecha_entrega_real=fecha_real,
    )

    assert minutos == 1441
    assert dias == 2
    assert monto == Decimal("110000.00")


def test_entregar_auto_guarda_recargo_devolucion_tardia(db_session):
    propietario = _crear_usuario(db_session, "prop.con-recargo@autospot.com", "PROPIETARIO")
    conductor = _crear_usuario(db_session, "cliente.con-recargo@autospot.com")
    vehiculo = _crear_vehiculo(db_session, propietario.id)

    reserva = Reserva(
        vehiculo_id=vehiculo.id,
        conductor_id=conductor.id,
        codigo="AS-RECAR",
        estado="EN_CURSO",
        monto_total=Decimal("50000.00"),
        fecha_inicio=datetime.now(timezone.utc) - timedelta(days=3),
        fecha_fin=datetime.now(timezone.utc) - timedelta(hours=1),
        fecha_salida_real=datetime.now(timezone.utc) - timedelta(days=2),
        estacion_retiro=vehiculo.estacion,
    )
    db_session.add(reserva)
    db_session.commit()

    actualizada = entregar_auto(
        db=db_session,
        reserva_id=reserva.id,
        conductor_id=conductor.id,
    )

    assert actualizada.estado == "ENTREGA_SOLICITADA"
    assert actualizada.fecha_entrega_solicitada is not None
    assert actualizada.minutos_retraso is not None
    assert actualizada.monto_penalizacion == Decimal("55000.00")
