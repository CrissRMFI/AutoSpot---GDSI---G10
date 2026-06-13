"""
Tests — US 16D: Dashboard de ganancias por vehículo.
"""
from datetime import datetime, timezone
from decimal import Decimal
import uuid

import pytest
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.exceptions import VehiculoNoEncontradoError
from app.main import app
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.services.ganancias import obtener_ganancias_vehiculo_propietario
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _registrar_y_loguear_usuario,
)


def _crear_usuario(db_session, email: str, rol: str = "PROPIETARIO") -> Usuario:
    usuario = Usuario(email=email, hashed_password="hash", rol=rol)
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


def _crear_vehiculo(
    db_session,
    propietario_id: uuid.UUID,
    patente: str,
) -> Vehiculo:
    vehiculo = Vehiculo(
        propietario_id=propietario_id,
        marca="Toyota",
        modelo="Corolla",
        anio=2021,
        tipo_transmision="AUTOMATICA",
        capacidad=5,
        categoria="SEDAN",
        tipo_combustible="NAFTA",
        pets_friendly=True,
        patente=patente,
        estacion="Estación Belgrano",
        precio_por_dia=Decimal("50000.00"),
        estado_registro="HABILITADO",
        disponible=True,
    )
    db_session.add(vehiculo)
    db_session.commit()
    db_session.refresh(vehiculo)
    return vehiculo


def _crear_reserva(
    db_session,
    vehiculo_id: uuid.UUID,
    conductor_id: uuid.UUID,
    monto_total: Decimal,
    estado: str,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    fecha_devolucion_real: datetime | None,
    fecha_salida_real: datetime | None = None,
) -> Reserva:
    reserva = Reserva(
        vehiculo_id=vehiculo_id,
        conductor_id=conductor_id,
        codigo=f"AS-{uuid.uuid4().hex[:8].upper()}",
        estado=estado,
        monto_total=monto_total,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        fecha_salida_real=fecha_salida_real,
        fecha_devolucion_real=fecha_devolucion_real,
        estacion_retiro="Estación Belgrano",
    )
    db_session.add(reserva)
    db_session.commit()
    db_session.refresh(reserva)
    return reserva


def test_ganancias_vehiculo_calcula_desglose_y_ocupacion_del_auto_seleccionado(db_session):
    propietario = _crear_usuario(db_session, "prop.us16d@autospot.com")
    otro_propietario = _crear_usuario(db_session, "otro-prop.us16d@autospot.com")
    conductor = _crear_usuario(db_session, "cliente.us16d@autospot.com", "CLIENTE")
    vehiculo = _crear_vehiculo(db_session, propietario.id, "UNI123")
    vehiculo_ajeno = _crear_vehiculo(db_session, otro_propietario.id, "OTR123")

    _crear_reserva(
        db_session,
        vehiculo.id,
        conductor.id,
        Decimal("100000.00"),
        "FINALIZADA",
        datetime(2026, 6, 1, 3, tzinfo=timezone.utc),
        datetime(2026, 6, 16, 3, tzinfo=timezone.utc),
        datetime(2026, 6, 16, 3, tzinfo=timezone.utc),
        fecha_salida_real=datetime(2026, 6, 1, 3, tzinfo=timezone.utc),
    )
    _crear_reserva(
        db_session,
        vehiculo.id,
        conductor.id,
        Decimal("50000.00"),
        "FINALIZADA",
        datetime(2026, 5, 10, 3, tzinfo=timezone.utc),
        datetime(2026, 5, 12, 3, tzinfo=timezone.utc),
        datetime(2026, 5, 12, 3, tzinfo=timezone.utc),
        fecha_salida_real=datetime(2026, 5, 10, 3, tzinfo=timezone.utc),
    )
    _crear_reserva(
        db_session,
        vehiculo.id,
        conductor.id,
        Decimal("90000.00"),
        "DEVUELTO",
        datetime(2026, 6, 20, 3, tzinfo=timezone.utc),
        datetime(2026, 6, 22, 3, tzinfo=timezone.utc),
        datetime(2026, 6, 22, 3, tzinfo=timezone.utc),
        fecha_salida_real=datetime(2026, 6, 20, 3, tzinfo=timezone.utc),
    )
    _crear_reserva(
        db_session,
        vehiculo_ajeno.id,
        conductor.id,
        Decimal("999999.00"),
        "FINALIZADA",
        datetime(2026, 6, 3, 3, tzinfo=timezone.utc),
        datetime(2026, 6, 6, 3, tzinfo=timezone.utc),
        datetime(2026, 6, 6, 3, tzinfo=timezone.utc),
        fecha_salida_real=datetime(2026, 6, 3, 3, tzinfo=timezone.utc),
    )

    reporte = obtener_ganancias_vehiculo_propietario(
        db=db_session,
        propietario_id=propietario.id,
        vehiculo_id=vehiculo.id,
        periodo="este_mes",
        ahora=datetime(2026, 6, 15, 12, tzinfo=timezone.utc),
    )

    assert reporte.vehiculo_id == str(vehiculo.id)
    assert reporte.patente == "UNI123"
    assert reporte.marca == "Toyota"
    assert reporte.modelo == "Corolla"
    assert reporte.categoria == "SEDAN"
    assert reporte.ingreso_bruto == Decimal("100000.00")
    assert reporte.comision_plataforma == Decimal("20000.00")
    assert reporte.ganancia_neta == Decimal("80000.00")
    assert reporte.ingreso_bruto_comparacion == Decimal("50000.00")
    assert reporte.porcentaje_variacion == Decimal("100.00")
    assert reporte.direccion_variacion == "SUBE"
    assert reporte.reservas_finalizadas == 1
    assert reporte.reservas_finalizadas_comparacion == 1
    assert reporte.dias_alquilados == Decimal("15.00")
    assert reporte.dias_disponibles == Decimal("30.00")
    assert reporte.tasa_ocupacion == Decimal("50.00")


def test_ganancias_vehiculo_esta_semana_usa_periodo_de_siete_dias(db_session):
    propietario = _crear_usuario(db_session, "prop-semana.us16d@autospot.com")
    conductor = _crear_usuario(db_session, "cliente-semana.us16d@autospot.com", "CLIENTE")
    vehiculo = _crear_vehiculo(db_session, propietario.id, "SEM123")

    _crear_reserva(
        db_session,
        vehiculo.id,
        conductor.id,
        Decimal("70000.00"),
        "FINALIZADA",
        datetime(2026, 6, 8, 3, tzinfo=timezone.utc),
        datetime(2026, 6, 15, 3, tzinfo=timezone.utc),
        datetime(2026, 6, 15, 2, tzinfo=timezone.utc),
        fecha_salida_real=datetime(2026, 6, 8, 3, tzinfo=timezone.utc),
    )

    reporte = obtener_ganancias_vehiculo_propietario(
        db=db_session,
        propietario_id=propietario.id,
        vehiculo_id=vehiculo.id,
        periodo="esta_semana",
        ahora=datetime(2026, 6, 13, 12, tzinfo=timezone.utc),
    )

    assert reporte.ingreso_bruto == Decimal("70000.00")
    assert reporte.dias_disponibles == Decimal("7.00")
    assert reporte.dias_alquilados == Decimal("6.96")
    assert reporte.tasa_ocupacion == Decimal("99.43")


def test_ganancias_vehiculo_rechaza_auto_ajeno(db_session):
    propietario = _crear_usuario(db_session, "prop-ajeno.us16d@autospot.com")
    otro_propietario = _crear_usuario(db_session, "otro-ajeno.us16d@autospot.com")
    vehiculo_ajeno = _crear_vehiculo(db_session, otro_propietario.id, "AJN123")

    with pytest.raises(VehiculoNoEncontradoError):
        obtener_ganancias_vehiculo_propietario(
            db=db_session,
            propietario_id=propietario.id,
            vehiculo_id=vehiculo_ajeno.id,
            periodo="este_mes",
            ahora=datetime(2026, 6, 15, 12, tzinfo=timezone.utc),
        )


def _insertar_reserva_vehiculo_http(engine, propietario_id: str) -> str:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        conductor = Usuario(
            email="cliente-http.us16d@autospot.com",
            hashed_password="hash",
            rol="CLIENTE",
        )
        db.add(conductor)
        db.flush()

        vehiculo = _crear_vehiculo(db, uuid.UUID(propietario_id), "HTTP16")
        reserva = Reserva(
            vehiculo_id=vehiculo.id,
            conductor_id=conductor.id,
            codigo="AS-US16D",
            estado="FINALIZADA",
            monto_total=Decimal("120000.00"),
            fecha_inicio=datetime.now(timezone.utc),
            fecha_fin=datetime.now(timezone.utc),
            fecha_devolucion_real=datetime.now(timezone.utc),
            estacion_retiro="Estación Belgrano",
        )
        db.add(reserva)
        db.commit()
        return str(vehiculo.id)


def test_endpoint_ganancias_vehiculo_requiere_propietario_autenticado():
    engine, client_context = _crear_cliente()
    try:
        with client_context as client:
            propietario_id, token = _registrar_y_loguear_usuario(
                client,
                "prop-http.us16d@autospot.com",
                rol="PROPIETARIO",
            )
            vehiculo_id = _insertar_reserva_vehiculo_http(engine, propietario_id)

            response = client.get(
                f"/vehiculos/{vehiculo_id}/ganancias?periodo=este_mes",
                headers=_auth_headers(token),
            )

            assert response.status_code == 200, response.text
            body = response.json()
            assert body["vehiculo_id"] == vehiculo_id
            assert body["patente"] == "HTTP16"
            assert Decimal(str(body["ingreso_bruto"])) == Decimal("120000.00")
            assert Decimal(str(body["comision_plataforma"])) == Decimal("24000.00")
            assert Decimal(str(body["ganancia_neta"])) == Decimal("96000.00")
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()
