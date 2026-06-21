"""
Tests — US 15D: Dashboard de ganancias generales.
"""
from datetime import datetime, timezone
from decimal import Decimal
import uuid

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.services.ganancias import obtener_ganancias_generales_propietario
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _login_usuario,
    _registrar_y_loguear_usuario,
)


def _crear_usuario(db_session, email: str, rol: str = "PROPIETARIO") -> Usuario:
    usuario = Usuario(email=email, hashed_password="hash", rol=rol)
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


def _crear_vehiculo(db_session, propietario_id: uuid.UUID) -> Vehiculo:
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
        kilometros=50000,
        patente="GAN123",
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
    fecha_devolucion_real: datetime | None,
) -> Reserva:
    fecha_base = fecha_devolucion_real or datetime(2026, 6, 10, tzinfo=timezone.utc)
    reserva = Reserva(
        vehiculo_id=vehiculo_id,
        conductor_id=conductor_id,
        codigo=f"AS-{uuid.uuid4().hex[:6].upper()}",
        estado=estado,
        monto_total=monto_total,
        fecha_inicio=fecha_base,
        fecha_fin=fecha_base,
        fecha_devolucion_real=fecha_devolucion_real,
        estacion_retiro="Estación Belgrano",
    )
    db_session.add(reserva)
    db_session.commit()
    db_session.refresh(reserva)
    return reserva


def test_ganancias_generales_calcula_80_20_y_filtra_por_propietario_periodo_y_estado(db_session):
    propietario = _crear_usuario(db_session, "prop.us15d@autospot.com")
    otro_propietario = _crear_usuario(db_session, "otro.us15d@autospot.com")
    conductor = _crear_usuario(db_session, "cliente.us15d@autospot.com", "CLIENTE")
    vehiculo = _crear_vehiculo(db_session, propietario.id)
    vehiculo_ajeno = _crear_vehiculo(db_session, otro_propietario.id)

    _crear_reserva(
        db_session,
        vehiculo.id,
        conductor.id,
        Decimal("100000.00"),
        "FINALIZADA",
        datetime(2026, 6, 8, 15, tzinfo=timezone.utc),
    )
    _crear_reserva(
        db_session,
        vehiculo.id,
        conductor.id,
        Decimal("50000.00"),
        "FINALIZADA",
        datetime(2026, 6, 12, 15, tzinfo=timezone.utc),
    )
    _crear_reserva(
        db_session,
        vehiculo.id,
        conductor.id,
        Decimal("100000.00"),
        "FINALIZADA",
        datetime(2026, 5, 20, 15, tzinfo=timezone.utc),
    )
    _crear_reserva(
        db_session,
        vehiculo.id,
        conductor.id,
        Decimal("90000.00"),
        "DEVUELTO",
        datetime(2026, 6, 13, 15, tzinfo=timezone.utc),
    )
    _crear_reserva(
        db_session,
        vehiculo_ajeno.id,
        conductor.id,
        Decimal("999999.00"),
        "FINALIZADA",
        datetime(2026, 6, 14, 15, tzinfo=timezone.utc),
    )

    reporte = obtener_ganancias_generales_propietario(
        db=db_session,
        propietario_id=propietario.id,
        periodo="este_mes",
        ahora=datetime(2026, 6, 15, 12, tzinfo=timezone.utc),
    )

    assert reporte.ingreso_bruto == Decimal("150000.00")
    assert reporte.comision_plataforma == Decimal("30000.00")
    assert reporte.ganancia_neta == Decimal("120000.00")
    assert reporte.ingreso_bruto_comparacion == Decimal("100000.00")
    assert reporte.porcentaje_variacion == Decimal("50.00")
    assert reporte.direccion_variacion == "SUBE"
    assert reporte.reservas_finalizadas == 2
    assert reporte.reservas_finalizadas_comparacion == 1
    assert len(reporte.evolucion_periodo) == 5
    assert reporte.evolucion_periodo[1].clave == "2026-06-08"
    assert reporte.evolucion_periodo[1].etiqueta == "Sem 2"
    assert reporte.evolucion_periodo[1].ingreso_bruto == Decimal("150000.00")
    assert reporte.evolucion_periodo[1].ganancia_neta == Decimal("120000.00")


def test_ganancias_generales_sin_base_previa_informa_sin_comparacion(db_session):
    propietario = _crear_usuario(db_session, "prop-sin-base.us15d@autospot.com")
    conductor = _crear_usuario(db_session, "cliente-sin-base.us15d@autospot.com", "CLIENTE")
    vehiculo = _crear_vehiculo(db_session, propietario.id)
    _crear_reserva(
        db_session,
        vehiculo.id,
        conductor.id,
        Decimal("75000.00"),
        "FINALIZADA",
        datetime(2026, 6, 3, 15, tzinfo=timezone.utc),
    )

    reporte = obtener_ganancias_generales_propietario(
        db=db_session,
        propietario_id=propietario.id,
        periodo="este_mes",
        ahora=datetime(2026, 6, 15, 12, tzinfo=timezone.utc),
    )

    assert reporte.porcentaje_variacion is None
    assert reporte.direccion_variacion == "SIN_COMPARACION"


def _insertar_reserva_finalizada_http(engine, propietario_id: str) -> None:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        conductor = Usuario(
            email="cliente-http.us15d@autospot.com",
            hashed_password="hash",
            rol="CLIENTE",
        )
        db.add(conductor)
        db.flush()
        vehiculo = _crear_vehiculo(db, uuid.UUID(propietario_id))
        reserva = Reserva(
            vehiculo_id=vehiculo.id,
            conductor_id=conductor.id,
            codigo="AS-US15D",
            estado="FINALIZADA",
            monto_total=Decimal("100000.00"),
            fecha_inicio=datetime(2026, 6, 1, 10, tzinfo=timezone.utc),
            fecha_fin=datetime(2026, 6, 3, 10, tzinfo=timezone.utc),
            fecha_devolucion_real=datetime.now(timezone.utc),
            estacion_retiro="Estación Belgrano",
        )
        db.add(reserva)
        db.commit()


class TestUS15DHTTP:
    def test_endpoint_ganancias_generales_requiere_propietario_autenticado(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_id, token = _registrar_y_loguear_usuario(
                    client,
                    "prop-http.us15d@autospot.com",
                    rol="PROPIETARIO",
                )
                _insertar_reserva_finalizada_http(engine, propietario_id)

                response = client.get(
                    f"/usuarios/{propietario_id}/ganancias-generales?periodo=este_mes",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                body = response.json()
                assert Decimal(str(body["ingreso_bruto"])) == Decimal("100000.00")
                assert Decimal(str(body["comision_plataforma"])) == Decimal("20000.00")
                assert Decimal(str(body["ganancia_neta"])) == Decimal("80000.00")
                assert body["fecha_imputacion"] == "fecha_devolucion_real"
                assert len(body["evolucion_periodo"]) == 5
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_endpoint_ganancias_generales_rechaza_recurso_ajeno(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_id, _ = _registrar_y_loguear_usuario(
                    client,
                    "prop-ajeno.us15d@autospot.com",
                    rol="PROPIETARIO",
                )
                _, token_otro = _registrar_y_loguear_usuario(
                    client,
                    "otro-prop.us15d@autospot.com",
                    rol="PROPIETARIO",
                )

                response = client.get(
                    f"/usuarios/{propietario_id}/ganancias-generales",
                    headers=_auth_headers(token_otro),
                )

                assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_endpoint_ganancias_generales_rechaza_cliente(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                propietario_id, _ = _registrar_y_loguear_usuario(
                    client,
                    "prop-cliente.us15d@autospot.com",
                    rol="PROPIETARIO",
                )
                _registrar_y_loguear_usuario(
                    client,
                    "cliente-no-prop.us15d@autospot.com",
                    rol="CLIENTE",
                )
                token_cliente = _login_usuario(client, "cliente-no-prop.us15d@autospot.com")

                response = client.get(
                    f"/usuarios/{propietario_id}/ganancias-generales",
                    headers=_auth_headers(token_cliente),
                )

                assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
