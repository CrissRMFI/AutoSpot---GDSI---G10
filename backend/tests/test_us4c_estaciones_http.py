"""
Tests de Integración HTTP — US 4C: Visualización y selección de estación.

Metodología: TDD (Fase Verde - Integración).

Criterios de Aceptación:
    CA 1: La solicitud de exploración incluye únicamente Estaciones activas.
    CA 2 (Listado): El sistema incluye las Estaciones en una lista.
    CA 3: Al seleccionar un punto de retiro específico, se suministra la dirección y las instrucciones de acceso para el Activo.

Además: cobertura del endpoint PATCH /estaciones/{id}/imagen (administración Postman).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.estacion import Estacion


_ENDPOINT_ESTACIONES = "/estaciones"


def _sembrar_estaciones(client: TestClient) -> Session:
    """Inserta estaciones de prueba en la DB sobreescrita por el fixture `client`."""
    from app.database import get_db
    from app.main import app

    override = app.dependency_overrides[get_db]
    db_gen = override()
    db: Session = next(db_gen)

    db.add_all([
        Estacion(
            id=1, nombre="Estación Palermo", direccion="Honduras 5500",
            instrucciones_acceso="Retiro keyless en subsuelo",
            zona="Palermo", activa=True,
        ),
        Estacion(
            id=2, nombre="Estación Recoleta", direccion="Av. Callao 1000",
            instrucciones_acceso="Ingreso por rampa vehicular",
            zona="Recoleta", activa=True,
        ),
        Estacion(
            id=3, nombre="Estación Mantenimiento", direccion="Taller Central",
            instrucciones_acceso="Prohibido el paso de Conductores",
            zona="Talleres", activa=False,
        ),
    ])
    db.commit()
    return db


class TestCA1yCA2_ListarEstacionesActivasHTTP:
    """
    Verifica que el sistema procesa la solicitud de exploración devolviendo
    una lista (CA2) que incluye únicamente aquellas estaciones operativas (CA1).
    """

    def test_listar_estaciones_devuelve_lista_solo_activas(self, client: TestClient):
        _sembrar_estaciones(client)

        response = client.get(f"{_ENDPOINT_ESTACIONES}/")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2

        for estacion in data:
            assert estacion["activa"] is True


class TestCA3_DetalleEstacionHTTP:
    """
    Verifica que al acceder a la información de la estación, el sistema suministra
    la dirección exacta y las instrucciones de acceso necesarias para el Conductor.
    """

    def test_obtener_detalle_estacion_existente_devuelve_200(self, client: TestClient):
        _sembrar_estaciones(client)

        response = client.get(f"{_ENDPOINT_ESTACIONES}/1")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == 1
        assert data["direccion"] == "Honduras 5500"
        assert data["instrucciones_acceso"] == "Retiro keyless en subsuelo"
        assert data["imagen_url"] is None

    def test_obtener_detalle_estacion_inexistente_devuelve_404(self, client: TestClient):
        _sembrar_estaciones(client)

        response = client.get(f"{_ENDPOINT_ESTACIONES}/999")

        assert response.status_code == 404
        assert response.json() == {"detail": "Estación no encontrada"}

    def test_obtener_detalle_estacion_inactiva_devuelve_404(self, client: TestClient):
        _sembrar_estaciones(client)

        response = client.get(f"{_ENDPOINT_ESTACIONES}/3")

        assert response.status_code == 404
        assert response.json() == {"detail": "La estación no está activa"}


class TestPatchImagenEstacionHTTP:
    """
    Verifica el endpoint administrativo PATCH /estaciones/{id}/imagen.
    """

    def test_actualizar_imagen_devuelve_200_y_persiste_url(self, client: TestClient):
        _sembrar_estaciones(client)

        nueva_url = "https://cdn.autospot.local/palermo.jpg"
        response = client.patch(
            f"{_ENDPOINT_ESTACIONES}/1/imagen",
            json={"imagen_url": nueva_url},
        )

        assert response.status_code == 200
        assert response.json()["imagen_url"] == nueva_url

        verificacion = client.get(f"{_ENDPOINT_ESTACIONES}/1")
        assert verificacion.json()["imagen_url"] == nueva_url

    def test_actualizar_imagen_a_null_limpia_la_url(self, client: TestClient):
        _sembrar_estaciones(client)

        # primero se setea
        client.patch(
            f"{_ENDPOINT_ESTACIONES}/1/imagen",
            json={"imagen_url": "https://cdn.autospot.local/old.jpg"},
        )

        # ahora se limpia
        response = client.patch(
            f"{_ENDPOINT_ESTACIONES}/1/imagen",
            json={"imagen_url": None},
        )

        assert response.status_code == 200
        assert response.json()["imagen_url"] is None

    def test_actualizar_imagen_estacion_inexistente_devuelve_404(self, client: TestClient):
        response = client.patch(
            f"{_ENDPOINT_ESTACIONES}/999/imagen",
            json={"imagen_url": "https://cdn.autospot.local/x.jpg"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Estación no encontrada"}

    def test_actualizar_imagen_payload_invalido_devuelve_422(self, client: TestClient):
        _sembrar_estaciones(client)

        response = client.patch(
            f"{_ENDPOINT_ESTACIONES}/1/imagen",
            json={"imagen_url": "no-es-una-url"},
        )

        assert response.status_code == 422