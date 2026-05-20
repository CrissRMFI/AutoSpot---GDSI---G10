"""
Tests unitarios de servicio — US 4C: Visualización y selección de estación.

Usa el fixture `db_session` de conftest.py: PostgreSQL `autospot_test_db` con
schema recreado por cada test (paridad con el entorno real y sin pisar la BD
de desarrollo ni la de producción).
"""
import pytest
from fastapi import HTTPException

from app.models.estacion import Estacion
from app.services import estacion_service


def _crear_estaciones_basicas(db):
    db.add_all([
        Estacion(
            id=1,
            nombre="Estacion A",
            direccion="Dir A",
            instrucciones_acceso="Inst A",
            zona="Zona A",
            activa=True,
        ),
        Estacion(
            id=2,
            nombre="Estacion B",
            direccion="Dir B",
            instrucciones_acceso="Inst B",
            zona="Zona B",
            activa=True,
        ),
        Estacion(
            id=3,
            nombre="Estacion Inactiva",
            direccion="Dir C",
            instrucciones_acceso="Inst C",
            zona="Zona C",
            activa=False,
        ),
    ])
    db.commit()


def test_get_estaciones_activas_solo_devuelve_activas(db_session):
    _crear_estaciones_basicas(db_session)

    activas = estacion_service.get_estaciones_activas(db_session)

    assert len(activas) == 2
    assert {e.id for e in activas} == {1, 2}
    assert all(e.activa for e in activas)


def test_get_estacion_by_id_devuelve_estacion_activa(db_session):
    _crear_estaciones_basicas(db_session)

    estacion = estacion_service.get_estacion_by_id(db_session, estacion_id=1)

    assert estacion.id == 1
    assert estacion.direccion == "Dir A"
    assert estacion.instrucciones_acceso == "Inst A"


def test_get_estacion_by_id_inexistente_lanza_404(db_session):
    _crear_estaciones_basicas(db_session)

    with pytest.raises(HTTPException) as exc:
        estacion_service.get_estacion_by_id(db_session, estacion_id=999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Estación no encontrada"


def test_get_estacion_by_id_inactiva_lanza_404(db_session):
    _crear_estaciones_basicas(db_session)

    with pytest.raises(HTTPException) as exc:
        estacion_service.get_estacion_by_id(db_session, estacion_id=3)

    assert exc.value.status_code == 404
    assert exc.value.detail == "La estación no está activa"


def test_actualizar_imagen_estacion_setea_url(db_session):
    _crear_estaciones_basicas(db_session)

    nueva_url = "https://cdn.autospot.local/estaciones/1.jpg"
    estacion = estacion_service.actualizar_imagen_estacion(
        db_session, estacion_id=1, imagen_url=nueva_url
    )

    assert estacion.imagen_url == nueva_url
    refrescada = db_session.query(Estacion).filter(Estacion.id == 1).first()
    assert refrescada.imagen_url == nueva_url


def test_actualizar_imagen_estacion_permite_limpiar(db_session):
    db_session.add(
        Estacion(
            id=1,
            nombre="Estacion A",
            direccion="Dir A",
            instrucciones_acceso="Inst A",
            zona="Zona A",
            activa=True,
            imagen_url="https://cdn.autospot.local/old.jpg",
        )
    )
    db_session.commit()

    estacion = estacion_service.actualizar_imagen_estacion(
        db_session, estacion_id=1, imagen_url=None
    )

    assert estacion.imagen_url is None


def test_actualizar_imagen_estacion_inexistente_lanza_404(db_session):
    with pytest.raises(HTTPException) as exc:
        estacion_service.actualizar_imagen_estacion(
            db_session, estacion_id=999, imagen_url="https://x"
        )

    assert exc.value.status_code == 404
