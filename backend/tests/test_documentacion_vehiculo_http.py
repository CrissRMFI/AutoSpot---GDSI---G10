"""
Tests HTTP — Cargar documentación legal del vehículo.

Endpoint:
    PATCH /vehiculos/{vehiculo_id}/documentacion

Contrato actual:
    - Requiere JWT.
    - Solo el propietario del vehículo puede cargar documentación.
"""
import uuid

from app.schemas.usuario import RegistroUsuarioSchema
from app.schemas.vehiculo import FotoVehiculoSchema, RegistroVehiculoSchema
from app.services.usuario import crear_usuario
from app.services.vehiculo import registrar_vehiculo
from app.utils.security import crear_access_token


def crear_vehiculo_base(db_session):
    """
    Helper para crear un vehículo válido usando la capa de servicio.
    """
    propietario = crear_usuario(
        db=db_session,
        schema=RegistroUsuarioSchema(
            email="propietario.documentacion.http@autospot.com",
            password="password123",
        ),
    )

    vehiculo = registrar_vehiculo(
        db=db_session,
        schema=RegistroVehiculoSchema(
            propietario_id=propietario.id,
            marca="Toyota",
            modelo="Corolla",
            anio=2020,
            tipo_transmision="AUTOMATICA",
            capacidad=5,
            categoria="SEDAN",
            tipo_combustible="NAFTA",
            pets_friendly=True,
            fotos=[
                FotoVehiculoSchema(
                    lado="FRENTE",
                    url="uploads/vehiculos/corolla/frente.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="TRASERA",
                    url="uploads/vehiculos/corolla/trasera.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_IZQUIERDO",
                    url="uploads/vehiculos/corolla/lateral_izquierdo.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_DERECHO",
                    url="uploads/vehiculos/corolla/lateral_derecho.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="INTERIOR",
                    url="uploads/vehiculos/corolla/interior.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
            ],
        ),
    )

    token = crear_access_token({"sub": str(propietario.id)})

    return vehiculo, token


def auth_headers(token: str) -> dict:
    """
    Helper para construir headers HTTP con Bearer token.
    """
    return {
        "Authorization": f"Bearer {token}",
    }


def payload_documentacion_valido():
    return {
        "patente": "ABC123",
        "chasis": "CHASIS123",
        "motor": "MOTOR123",
        "titular": "Juan Propietario",
        "cedula": "cedula.pdf",
        "poliza": "poliza.pdf",
        "vtv": "vtv.pdf",
        "estacion": "Palermo",
        "telefono": "1122334455",
        "descripcion": "Documentación cargada para revisión.",
    }


class TestCargaDocumentacionVehiculoHTTP:
    """
    Verifica el happy path del endpoint documental.
    """

    def test_carga_documentacion_legal_devuelve_200(
        self,
        client,
        db_session,
    ):
        vehiculo, token = crear_vehiculo_base(db_session)

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion",
            json=payload_documentacion_valido(),
            headers=auth_headers(token),
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(vehiculo.id)
        assert body["patente"] == "ABC123"
        assert body["chasis"] == "CHASIS123"
        assert body["motor"] == "MOTOR123"
        assert body["titular"] == "Juan Propietario"
        assert body["cedula"] == "cedula.pdf"
        assert body["poliza"] == "poliza.pdf"
        assert body["vtv"] == "vtv.pdf"
        assert body["estacion"] == "Palermo"
        assert body["telefono"] == "1122334455"
        assert body["descripcion"] == "Documentación cargada para revisión."
        assert body["estado_registro"] == "EN_REVISION"

    def test_no_permite_cargar_documentacion_si_vehiculo_habilitado(
        self,
        client,
        db_session,
    ):
        vehiculo, token = crear_vehiculo_base(db_session)
        vehiculo.estado_registro = "HABILITADO"
        db_session.commit()

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion",
            json=payload_documentacion_valido(),
            headers=auth_headers(token),
        )

        assert response.status_code == 409
        assert "no puede modificarse" in response.json()["detail"]

    def test_permite_corregir_documentacion_si_vehiculo_rechazado(
        self,
        client,
        db_session,
    ):
        vehiculo, token = crear_vehiculo_base(db_session)
        vehiculo.estado_registro = "RECHAZADO"
        vehiculo.motivo_rechazo = "Documento ilegible"
        db_session.commit()

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion",
            json=payload_documentacion_valido(),
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        assert response.json()["estado_registro"] == "EN_REVISION"


class TestErroresDocumentacionVehiculoHTTP:
    """
    Verifica errores HTTP del endpoint documental.
    """

    def test_sin_token_devuelve_401(self, client, db_session):
        vehiculo, _ = crear_vehiculo_base(db_session)

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion",
            json=payload_documentacion_valido(),
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "No autenticado"

    def test_vehiculo_inexistente_devuelve_404(self, client, db_session):
        _, token = crear_vehiculo_base(db_session)

        response = client.patch(
            f"/vehiculos/{uuid.uuid4()}/documentacion",
            json=payload_documentacion_valido(),
            headers=auth_headers(token),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Vehiculo no encontrado"

    def test_payload_con_campo_obligatorio_vacio_devuelve_422(
        self,
        client,
        db_session,
    ):
        vehiculo, token = crear_vehiculo_base(db_session)
        payload = payload_documentacion_valido()
        payload["patente"] = ""

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion",
            json=payload,
            headers=auth_headers(token),
        )

        assert response.status_code == 422
        assert "Campo obligatorio" in str(response.json())

    def test_payload_sin_campo_obligatorio_devuelve_422(
        self,
        client,
        db_session,
    ):
        vehiculo, token = crear_vehiculo_base(db_session)
        payload = payload_documentacion_valido()
        payload.pop("poliza")

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion",
            json=payload,
            headers=auth_headers(token),
        )

        assert response.status_code == 422
