"""
Tests unitarios de la US 15C: Registro del estado inicial del activo (Check-in).
"""
import uuid
import pytest
from pydantic import ValidationError

from app.schemas.checkin_vehiculo import CheckinCreatePayloadSchema
from app.services.checkin_service import (
    crear_checkin,
    obtener_checkin_de_reserva_conductor,
    re_enviar_checkin,
)
from app.models.reserva import Reserva
from app.models.checkin_vehiculo import CheckinVehiculo
from fastapi import HTTPException


def test_schema_exito_sin_danios():
    """Test unitario Pydantic: Checkin exitoso sin daños"""
    payload = CheckinCreatePayloadSchema(
        reserva_id=uuid.uuid4(),
        nivel_combustible="Lleno",
        kilometraje_actual=1000,
        esta_limpio=True,
        tiene_danios=False,
        descripcion_danios=None,
        url_foto_frente="url1",
        url_foto_trasera="url2",
        url_foto_lateral_izq="url3",
        url_foto_lateral_der="url4",
        url_foto_panel="url5",
        urls_fotos_danios=[],
    )
    assert payload.tiene_danios is False


def test_schema_falla_con_danios_sin_descripcion_ni_fotos():
    """Test unitario Pydantic: Si tiene daños debe enviar descripción y fotos."""
    with pytest.raises(ValidationError) as exc:
        CheckinCreatePayloadSchema(
            reserva_id=uuid.uuid4(),
            nivel_combustible="Lleno",
            kilometraje_actual=1000,
            esta_limpio=True,
            tiene_danios=True,  # Daño marcado pero sin descripcion ni foto
            descripcion_danios=None,
            url_foto_frente="url1",
            url_foto_trasera="url2",
            url_foto_lateral_izq="url3",
            url_foto_lateral_der="url4",
            url_foto_panel="url5",
            urls_fotos_danios=[],
        )
    assert "Debe proveer una descripción si indica que hay daños" in str(exc.value)


class MockQuery:
    def __init__(self, result):
        self.result = result
    def filter(self, *args, **kwargs):
        return self
    def options(self, *args, **kwargs):
        return self
    def first(self):
        return self.result


class MockDB:
    def __init__(self, queries):
        self.queries = queries
        self.adds = []
        self._query_idx = 0

    def query(self, model):
        result = self.queries[self._query_idx]
        self._query_idx += 1
        return MockQuery(result)

    def add(self, obj):
        self.adds.append(obj)

    def flush(self):
        pass

    def commit(self):
        pass

    def refresh(self, obj):
        pass


def test_crear_checkin_falla_si_reserva_no_verificada():
    """Test de regla de negocio: no se puede hacer check-in de reserva no verificada"""
    reserva_mock = Reserva(id=uuid.uuid4(), conductor_id=uuid.uuid4(), estado="CONFIRMADA")
    db_mock = MockDB(queries=[reserva_mock])

    payload = CheckinCreatePayloadSchema(
        reserva_id=reserva_mock.id,
        nivel_combustible="Lleno",
        kilometraje_actual=100,
        esta_limpio=True,
        tiene_danios=False,
        url_foto_frente="a", url_foto_trasera="b", url_foto_lateral_izq="c", url_foto_lateral_der="d", url_foto_panel="e",
    )

    with pytest.raises(HTTPException) as exc:
        crear_checkin(db=db_mock, schema=payload, conductor_id=reserva_mock.conductor_id)
    assert exc.value.status_code == 400
    assert "Solo se puede hacer check-in de una reserva VERIFICADA" in str(exc.value.detail)


@pytest.mark.parametrize(
    ("estado", "mensaje"),
    [
        ("PENDIENTE", "Ya enviaste el check-in de esta reserva"),
        ("APROBADO", "ya fue aprobado"),
        ("RECHAZADO", "Debés reenviar la corrección"),
    ],
)
def test_crear_checkin_falla_si_ya_existe_checkin(estado, mensaje):
    """No se puede crear otro check-in si la reserva ya tiene uno."""
    conductor_id = uuid.uuid4()
    reserva_mock = Reserva(id=uuid.uuid4(), conductor_id=conductor_id, estado="VERIFICADA")
    checkin_mock = CheckinVehiculo(
        id=uuid.uuid4(),
        reserva_id=reserva_mock.id,
        conductor_id=conductor_id,
        estado=estado,
    )
    db_mock = MockDB(queries=[reserva_mock, checkin_mock])

    payload = CheckinCreatePayloadSchema(
        reserva_id=reserva_mock.id,
        nivel_combustible="Lleno",
        kilometraje_actual=100,
        esta_limpio=True,
        tiene_danios=False,
        url_foto_frente="a", url_foto_trasera="b", url_foto_lateral_izq="c", url_foto_lateral_der="d", url_foto_panel="e",
    )

    with pytest.raises(HTTPException) as exc:
        crear_checkin(db=db_mock, schema=payload, conductor_id=conductor_id)

    assert exc.value.status_code == 400
    assert mensaje in str(exc.value.detail)


def test_re_enviar_checkin_falla_si_no_rechazado():
    """Test de regla de negocio: no se puede editar un check-in que no está rechazado."""
    checkin_mock = CheckinVehiculo(id=uuid.uuid4(), conductor_id=uuid.uuid4(), estado="APROBADO")
    db_mock = MockDB(queries=[checkin_mock])

    payload = CheckinCreatePayloadSchema(
        reserva_id=uuid.uuid4(),
        nivel_combustible="Lleno",
        kilometraje_actual=100,
        esta_limpio=True,
        tiene_danios=False,
        url_foto_frente="a", url_foto_trasera="b", url_foto_lateral_izq="c", url_foto_lateral_der="d", url_foto_panel="e",
    )

    with pytest.raises(HTTPException) as exc:
        re_enviar_checkin(db=db_mock, checkin_id=checkin_mock.id, schema=payload, conductor_id=checkin_mock.conductor_id)
    assert exc.value.status_code == 400
    assert "Solo se pueden editar check-ins en estado RECHAZADO" in str(exc.value.detail)


def test_obtener_checkin_de_reserva_conductor_devuelve_checkin_propio():
    """El conductor puede consultar el check-in existente de su reserva."""
    conductor_id = uuid.uuid4()
    reserva_mock = Reserva(id=uuid.uuid4(), conductor_id=conductor_id, estado="VERIFICADA")
    checkin_mock = CheckinVehiculo(
        id=uuid.uuid4(),
        reserva_id=reserva_mock.id,
        conductor_id=conductor_id,
        estado="PENDIENTE",
    )
    db_mock = MockDB(queries=[reserva_mock, checkin_mock])

    resultado = obtener_checkin_de_reserva_conductor(
        db=db_mock,
        reserva_id=reserva_mock.id,
        conductor_id=conductor_id,
    )

    assert resultado is checkin_mock


def test_obtener_checkin_de_reserva_conductor_falla_si_reserva_ajena():
    """No se expone el check-in de una reserva de otro conductor."""
    reserva_mock = Reserva(id=uuid.uuid4(), conductor_id=uuid.uuid4(), estado="VERIFICADA")
    db_mock = MockDB(queries=[reserva_mock])

    with pytest.raises(HTTPException) as exc:
        obtener_checkin_de_reserva_conductor(
            db=db_mock,
            reserva_id=reserva_mock.id,
            conductor_id=uuid.uuid4(),
        )

    assert exc.value.status_code == 403
