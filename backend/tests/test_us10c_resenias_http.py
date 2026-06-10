import uuid
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from decimal import Decimal

from app.models.usuario import Usuario
from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.models.vehiculo import Vehiculo
from app.models.reserva import Reserva
from app.models.valoracion import Valoracion
from app.models.testimonio import Testimonio
from app.dependencies.auth import get_usuario_actual
from app.main import app

def test_get_resenias_exito(client: TestClient, db_session):
    """
    Verifica que el endpoint GET /vehiculos/{vehiculo_id}/resenias responda con 200 OK
    y devuelva la reseña creada.
    """
    propietario = Usuario(email="prop@a.com", hashed_password="123")
    conductor = Usuario(email="cond@a.com", hashed_password="123")
    db_session.add_all([propietario, conductor])
    db_session.flush()

    datos = DatosPersonalesUsuario(
        usuario_id=conductor.id, 
        dni="123", 
        nombre="Juan", 
        apellido="Perez", 
        foto_dni_frente_url="", 
        foto_dni_dorso_url=""
    )
    db_session.add(datos)
    db_session.flush()

    vehiculo = Vehiculo(
        propietario_id=propietario.id, 
        marca="Toyota", 
        modelo="Corolla", 
        anio=2020, 
        patente="AA123BB", 
        tipo_transmision="MANUAL", 
        capacidad=5, 
        categoria="SEDAN", 
        tipo_combustible="NAFTA", 
        pets_friendly=False,
        precio_por_dia=Decimal("1000")
    )
    db_session.add(vehiculo)
    db_session.flush()

    reserva = Reserva(
        vehiculo_id=vehiculo.id, 
        conductor_id=conductor.id, 
        codigo="TESTCODE123",
        fecha_inicio=datetime.now(timezone.utc), 
        fecha_fin=datetime.now(timezone.utc), 
        monto_total=Decimal("1000"), 
        estacion_retiro="Estación Central"
    )
    db_session.add(reserva)
    db_session.flush()

    val = Valoracion(reserva_id=reserva.id, conductor_id=conductor.id, vehiculo_id=vehiculo.id, puntaje=4)
    db_session.add(val)
    testimonio = Testimonio(reserva_id=reserva.id, conductor_id=conductor.id, vehiculo_id=vehiculo.id, descripcion="Muy buen vehículo")
    db_session.add(testimonio)
    db_session.commit()

    # Override auth
    app.dependency_overrides[get_usuario_actual] = lambda: {"sub": str(conductor.id)}

    try:
        response = client.get(f"/vehiculos/{vehiculo.id}/resenias")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["conductor"] == "Juan Perez"
        assert data[0]["puntaje"] == 4.0
        assert data[0]["descripcion"] == "Muy buen vehículo"
    finally:
        app.dependency_overrides.clear()


def test_get_resenias_vacia(client: TestClient, db_session):
    """
    Verifica que al consultar un vehículo que existe pero sin reseñas, 
    el endpoint devuelve 200 OK y una lista vacía.
    """
    propietario = Usuario(email="prop2@a.com", hashed_password="123")
    db_session.add(propietario)
    db_session.flush()

    vehiculo = Vehiculo(
        propietario_id=propietario.id, 
        marca="Ford", 
        modelo="Fiesta", 
        anio=2019, 
        patente="BB123CC", 
        tipo_transmision="MANUAL", 
        capacidad=5, 
        categoria="HATCHBACK", 
        tipo_combustible="NAFTA", 
        pets_friendly=False,
        precio_por_dia=Decimal("800")
    )
    db_session.add(vehiculo)
    db_session.commit()

    app.dependency_overrides[get_usuario_actual] = lambda: {"sub": str(propietario.id)}

    try:
        response = client.get(f"/vehiculos/{vehiculo.id}/resenias")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    finally:
        app.dependency_overrides.clear()


def test_get_resenias_vehiculo_no_encontrado(client: TestClient):
    """
    Verifica que al consultar un UUID de un vehículo que no existe,
    el endpoint devuelva 404 Not Found.
    """
    fake_id = uuid.uuid4()
    
    app.dependency_overrides[get_usuario_actual] = lambda: {"sub": str(uuid.uuid4())}

    try:
        response = client.get(f"/vehiculos/{fake_id}/resenias")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
