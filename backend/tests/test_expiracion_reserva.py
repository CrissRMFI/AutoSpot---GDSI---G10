import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo

# Dependiendo de si se expone un endpoint o si probaremos el servicio, el test 1 lo armaremos
# asumiendo un servicio expirar_reservas_vencidas o un endpoint.
# Como el requerimiento dice "endpoint o servicio", testearemos asumiendo la existencia
# de una función de servicio para mantener limpia la API, a menos que se exponga un endpoint cron.
from app.services.alquiler_service import expirar_reservas_vencidas


def test_expirar_reservas_y_liberar_vehiculo(db_session: Session):
    """
    Test 1: Verificar que un servicio marque la reserva como "EXPIRADO" y el
    auto como "DISPONIBLE" si la hora actual superó la (hora_inicio + 30 minutos)
    y el estado era "CONFIRMADA".
    """
    # 1. Preparar datos
    conductor = Usuario(
        id=uuid.uuid4(), email="conductor@test.com", hashed_password="hash", rol="CLIENTE"
    )
    propietario = Usuario(
        id=uuid.uuid4(), email="propietario@test.com", hashed_password="hash", rol="PROPIETARIO"
    )
    db_session.add_all([conductor, propietario])
    db_session.flush()

    vehiculo = Vehiculo(
        id=uuid.uuid4(),
        propietario_id=propietario.id,
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        tipo_transmision="Manual",
        capacidad=5,
        categoria="Sedan",
        tipo_combustible="Nafta",
        pets_friendly=True,
        estacion="Central",
        patente="TEST1234",
        disponible=False,
        precio_por_dia=10000,
    )
    db_session.add(vehiculo)
    db_session.commit()

    # Reserva vieja (ya pasaron más de 30 mins desde fecha_inicio)
    ahora = datetime.now(timezone.utc)
    reserva = Reserva(
        vehiculo_id=vehiculo.id,
        conductor_id=conductor.id,
        codigo="12345678",
        estado="CONFIRMADA",
        monto_total=10000,
        fecha_inicio=ahora - timedelta(minutes=35), # Inició hace 35 min
        fecha_fin=ahora + timedelta(days=1),
        estacion_retiro="Estacion Central",
    )
    db_session.add(reserva)
    db_session.commit()

    # 2. Ejecutar la acción (esperamos que esta función exista en el Step 3)
    expirar_reservas_vencidas(db_session)

    # 3. Verificar resultados
    db_session.refresh(reserva)
    db_session.refresh(vehiculo)

    assert reserva.estado == "EXPIRADO", "La reserva debería haber pasado a estado EXPIRADO"
    assert vehiculo.disponible == True, "El vehículo debería haberse liberado y estar DISPONIBLE"


def test_listar_mis_reservas_filtro_expirado(client: TestClient, db_session: Session):
    """
    Test 2: Verificar que el endpoint GET de reservas del usuario devuelva
    las reservas expiradas y permita filtrar por `?estado=EXPIRADO`.
    """
    # 1. Preparar datos (usuario autenticado y una reserva EXPIRADA)
    conductor = Usuario(
        id=uuid.uuid4(), email="conductor2@test.com", hashed_password="hash", rol="CLIENTE"
    )
    propietario = Usuario(
        id=uuid.uuid4(), email="propietario2@test.com", hashed_password="hash", rol="PROPIETARIO"
    )
    db_session.add_all([conductor, propietario])
    db_session.flush()

    vehiculo1 = Vehiculo(
        id=uuid.uuid4(),
        propietario_id=propietario.id,
        marca="Ford",
        modelo="Fiesta",
        anio=2020,
        tipo_transmision="Manual",
        capacidad=5,
        categoria="Hatchback",
        tipo_combustible="Nafta",
        pets_friendly=True,
        estacion="Sur",
        patente="EXP123",
        disponible=True,
        precio_por_dia=10000,
    )
    vehiculo2 = Vehiculo(
        id=uuid.uuid4(),
        propietario_id=propietario.id,
        marca="Chevrolet",
        modelo="Onix",
        anio=2021,
        tipo_transmision="Manual",
        capacidad=5,
        categoria="Hatchback",
        tipo_combustible="Nafta",
        pets_friendly=True,
        estacion="Sur",
        patente="PEN123",
        disponible=False,
        precio_por_dia=12000,
    )
    db_session.add_all([vehiculo1, vehiculo2])
    db_session.commit()

    reserva_expirada = Reserva(
        vehiculo_id=vehiculo1.id,
        conductor_id=conductor.id,
        codigo="EXPIRADA1",
        estado="EXPIRADO",
        monto_total=10000,
        fecha_inicio=datetime.now(timezone.utc) - timedelta(days=2),
        fecha_fin=datetime.now(timezone.utc) - timedelta(days=1),
        estacion_retiro="Estacion Sur",
    )
    
    reserva_activa = Reserva(
        vehiculo_id=vehiculo2.id,
        conductor_id=conductor.id,
        codigo="ACTIVA123",
        estado="CONFIRMADA",
        monto_total=10000,
        fecha_inicio=datetime.now(timezone.utc) + timedelta(days=1),
        fecha_fin=datetime.now(timezone.utc) + timedelta(days=2),
        estacion_retiro="Estacion Sur",
    )
    db_session.add_all([reserva_expirada, reserva_activa])
    db_session.commit()

    # Simulamos el token para el conductor
    # (En la suite real se debe mockear o generar el token, aquí asumimos la lógica estándar)
    from app.utils.security import crear_access_token
    token = crear_access_token({"sub": str(conductor.id), "rol": "CLIENTE"})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Consultar sin filtro (debería incluir la reserva expirada)
    response_todas = client.get("/alquiler/reservas", headers=headers)
    assert response_todas.status_code == 200
    data_todas = response_todas.json()
    assert any(r["id"] == str(reserva_expirada.id) for r in data_todas)
    assert any(r["estado"] == "EXPIRADO" for r in data_todas)

    # 3. Consultar con filtro ?estado=EXPIRADO
    response_filtrada = client.get("/alquiler/reservas?estado=EXPIRADO", headers=headers)
    assert response_filtrada.status_code == 200
    data_filtrada = response_filtrada.json()
    
    assert len(data_filtrada) == 1
    assert data_filtrada[0]["id"] == str(reserva_expirada.id)
    assert data_filtrada[0]["estado"] == "EXPIRADO"
