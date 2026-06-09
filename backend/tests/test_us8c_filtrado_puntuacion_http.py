"""
Tests HTTP — US 8C: Motor de filtrado de catálogo por puntuación.

Endpoint bajo prueba:
    GET /vehiculos/catalogo?puntuacion_minima=<n>

Criterios de Aceptación cubiertos:
    CA 1 — Al seleccionar una puntuación, el catálogo muestra únicamente los
           autos con esa puntuación o una mayor.
    CA 2 — El filtro por puntuación se intersecta con el resto de condiciones
           del catálogo (solo habilitados, disponibles y con precio).
    CA 3 — Si la combinación no coincide con ninguna unidad, se informa la
           inexistencia de coincidencias (lista vacía).
    CA 4 — Sin filtro, se devuelve el catálogo completo.

La puntuación de cada vehículo se fija directamente en la base (la generación
de la calificación es responsabilidad de US 17C); aquí solo se prueba el filtro.
"""
import uuid
from decimal import Decimal

from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.vehiculo import Vehiculo
from tests.test_us9d_habilitar_auto_http import (
    _auth_headers,
    _crear_cliente,
    _registrar_vehiculo,
    _registrar_y_loguear_usuario,
)
from tests.test_us14c_obtener_codigo_reserva_http import _hacer_vehiculo_reservable


def _calificar_vehiculo(engine, vehiculo_id: str, promedio) -> None:
    """Fija la calificación promedio de un vehículo directamente en la BD."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db:
        vehiculo = db.query(Vehiculo).filter(
            Vehiculo.id == uuid.UUID(vehiculo_id)
        ).first()
        vehiculo.calificacion_promedio = (
            Decimal(str(promedio)) if promedio is not None else None
        )
        db.commit()


def _crear_vehiculo_en_catalogo(client, engine, email: str, promedio) -> dict:
    """Crea un vehículo reservable (habilitado + disponible + precio) y lo califica."""
    vehiculo, _ = _registrar_vehiculo(client, email)
    _hacer_vehiculo_reservable(engine, vehiculo["id"])
    _calificar_vehiculo(engine, vehiculo["id"], promedio)
    return vehiculo


def _ids(data) -> set:
    return {v["id"] for v in data}


class TestCA1_FiltroPorPuntuacion:
    def test_filtra_solo_los_de_puntuacion_o_mayor(self):
        """CA 1: con puntuacion_minima=4 se devuelven solo los de 4 o más."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                bajo = _crear_vehiculo_en_catalogo(
                    client, engine, "prop-bajo@autospot.com", 2.0
                )
                medio = _crear_vehiculo_en_catalogo(
                    client, engine, "prop-medio@autospot.com", 3.5
                )
                alto = _crear_vehiculo_en_catalogo(
                    client, engine, "prop-alto@autospot.com", 4.5
                )

                _, token = _registrar_y_loguear_usuario(
                    client, "cli-ca1@autospot.com"
                )

                response = client.get(
                    "/vehiculos/catalogo",
                    params={"puntuacion_minima": 4},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                ids = _ids(response.json())
                assert alto["id"] in ids
                assert bajo["id"] not in ids
                assert medio["id"] not in ids
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_incluye_el_borde_exacto(self):
        """Un vehículo con calificación exactamente igual al filtro se incluye."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                exacto = _crear_vehiculo_en_catalogo(
                    client, engine, "prop-borde@autospot.com", 4.0
                )
                _, token = _registrar_y_loguear_usuario(
                    client, "cli-borde@autospot.com"
                )

                response = client.get(
                    "/vehiculos/catalogo",
                    params={"puntuacion_minima": 4},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                assert exacto["id"] in _ids(response.json())
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestCA2_InterseccionConDisponibilidad:
    def test_no_devuelve_vehiculo_bien_calificado_pero_no_disponible(self):
        """
        CA 2: el filtro por puntuación se intersecta con el resto de condiciones.
        Un vehículo con buena calificación pero NO disponible no aparece.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                # Bien calificado pero se lo marca como no disponible.
                vehiculo = _crear_vehiculo_en_catalogo(
                    client, engine, "prop-nodisp@autospot.com", 5.0
                )
                TestingSessionLocal = sessionmaker(
                    autocommit=False, autoflush=False, bind=engine
                )
                with TestingSessionLocal() as db:
                    v = db.query(Vehiculo).filter(
                        Vehiculo.id == uuid.UUID(vehiculo["id"])
                    ).first()
                    v.disponible = False
                    db.commit()

                _, token = _registrar_y_loguear_usuario(
                    client, "cli-ca2@autospot.com"
                )

                response = client.get(
                    "/vehiculos/catalogo",
                    params={"puntuacion_minima": 4},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                assert vehiculo["id"] not in _ids(response.json())
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestCA3_SinCoincidencias:
    def test_sin_coincidencias_devuelve_lista_vacia(self):
        """CA 3: si ningún vehículo alcanza la puntuación pedida, lista vacía."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _crear_vehiculo_en_catalogo(
                    client, engine, "prop-ca3a@autospot.com", 2.0
                )
                _crear_vehiculo_en_catalogo(
                    client, engine, "prop-ca3b@autospot.com", 3.0
                )
                _, token = _registrar_y_loguear_usuario(
                    client, "cli-ca3@autospot.com"
                )

                response = client.get(
                    "/vehiculos/catalogo",
                    params={"puntuacion_minima": 4.5},
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                assert response.json() == []
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestCA4_SinFiltro:
    def test_sin_filtro_devuelve_catalogo_completo(self):
        """CA 4: sin el parámetro, se devuelven todos (incluso sin calificar)."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                calificado = _crear_vehiculo_en_catalogo(
                    client, engine, "prop-ca4a@autospot.com", 5.0
                )
                sin_calificar = _crear_vehiculo_en_catalogo(
                    client, engine, "prop-ca4b@autospot.com", None
                )
                _, token = _registrar_y_loguear_usuario(
                    client, "cli-ca4@autospot.com"
                )

                response = client.get(
                    "/vehiculos/catalogo",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                ids = _ids(response.json())
                assert calificado["id"] in ids
                assert sin_calificar["id"] in ids
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()


class TestContratoApi:
    def test_catalogo_expone_calificacion_promedio(self):
        """La respuesta del catálogo expone el campo calificacion_promedio."""
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                vehiculo = _crear_vehiculo_en_catalogo(
                    client, engine, "prop-campo@autospot.com", 4.0
                )
                _, token = _registrar_y_loguear_usuario(
                    client, "cli-campo@autospot.com"
                )

                response = client.get(
                    "/vehiculos/catalogo",
                    headers=_auth_headers(token),
                )

                assert response.status_code == 200, response.text
                item = next(
                    v for v in response.json() if v["id"] == vehiculo["id"]
                )
                assert "calificacion_promedio" in item
                assert float(item["calificacion_promedio"]) == 4.0
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_puntuacion_mayor_a_5_devuelve_422(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client, "cli-422a@autospot.com"
                )
                response = client.get(
                    "/vehiculos/catalogo",
                    params={"puntuacion_minima": 6},
                    headers=_auth_headers(token),
                )
                assert response.status_code == 422, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_puntuacion_menor_a_1_devuelve_422(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                _, token = _registrar_y_loguear_usuario(
                    client, "cli-422b@autospot.com"
                )
                response = client.get(
                    "/vehiculos/catalogo",
                    params={"puntuacion_minima": 0},
                    headers=_auth_headers(token),
                )
                assert response.status_code == 422, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()

    def test_catalogo_sin_token_devuelve_401(self):
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                response = client.get(
                    "/vehiculos/catalogo",
                    params={"puntuacion_minima": 4},
                )
                assert response.status_code == 401, response.text
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
