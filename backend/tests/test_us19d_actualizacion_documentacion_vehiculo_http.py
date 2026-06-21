"""
Tests HTTP — US 19D: Actualizar documentación legal del vehículo.

Endpoint bajo prueba:
    PATCH /vehiculos/{vehiculo_id}/documentacion/actualizar

"""
import uuid
from datetime import datetime, timedelta, timezone

from app.schemas.usuario import RegistroUsuarioSchema
from app.schemas.vehiculo import FotoVehiculoSchema, RegistroVehiculoSchema
from app.services.usuario import crear_usuario
from app.services.vehiculo import registrar_vehiculo
from app.utils.security import crear_access_token
from app.models.reserva import Reserva


def crear_vehiculo_base(db_session):
    propietario = crear_usuario(
        db=db_session,
        schema=RegistroUsuarioSchema(
            email="propietario.actualizar.http@autospot.com",
            password="password123",
            rol="PROPIETARIO",
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
            kilometros=50000,
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
    return {"Authorization": f"Bearer {token}"}


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
        "descripcion": "Actualización documental.",
    }


class TestActualizacionDocumentacionVehiculoHTTP:
    def test_actualiza_documentacion_devuelve_200(self, client, db_session):
        vehiculo, token = crear_vehiculo_base(db_session)

        # Preparar vehículo en estado HABILITADO y no disponible
        vehiculo.estado_registro = "HABILITADO"
        vehiculo.disponible = False
        db_session.commit()

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion/actualizar",
            json=payload_documentacion_valido(),
            headers=auth_headers(token),
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == str(vehiculo.id)
        assert body["patente"] == "ABC123"
        assert body["estado_registro"] == "EN_REVISION"

    def test_sin_token_devuelve_401(self, client, db_session):
        vehiculo, _ = crear_vehiculo_base(db_session)

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion/actualizar",
            json=payload_documentacion_valido(),
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "No autenticado"

    def test_recurso_ajeno_devuelve_403(self, client, db_session):
        vehiculo, _ = crear_vehiculo_base(db_session)

        # crear otro propietario y token
        otro = crear_usuario(
            db=db_session,
            schema=RegistroUsuarioSchema(
                email="otro.propietario@autospot.com",
                password="password123",
                rol="PROPIETARIO",
            ),
        )
        token_otro = crear_access_token({"sub": str(otro.id)})

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion/actualizar",
            json=payload_documentacion_valido(),
            headers=auth_headers(token_otro),
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "No puede operar sobre un vehículo de otro usuario"

    def test_vehiculo_inexistente_devuelve_404(self, client, db_session):
        _, token = crear_vehiculo_base(db_session)

        response = client.patch(
            f"/vehiculos/{uuid.uuid4()}/documentacion/actualizar",
            json=payload_documentacion_valido(),
            headers=auth_headers(token),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Vehiculo no encontrado"

    def test_documentacion_no_existente_devuelve_404_si_no_habilitado(self, client, db_session):
        vehiculo, token = crear_vehiculo_base(db_session)

        # estado distinto a HABILITADO -> no existe documentación previa
        vehiculo.estado_registro = "RECHAZADO"
        db_session.commit()

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion/actualizar",
            json=payload_documentacion_valido(),
            headers=auth_headers(token),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No existe documentación previa para este vehículo"

    def test_payload_invalido_devuelve_422(self, client, db_session):
        vehiculo, token = crear_vehiculo_base(db_session)
        vehiculo.estado_registro = "HABILITADO"
        vehiculo.disponible = False
        db_session.commit()

        payload = payload_documentacion_valido()
        payload.pop("patente")

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion/actualizar",
            json=payload,
            headers=auth_headers(token),
        )

        assert response.status_code == 422

    def test_no_permite_actualizar_si_disponible_devuelve_400(self, client, db_session):
        vehiculo, token = crear_vehiculo_base(db_session)
        vehiculo.estado_registro = "HABILITADO"
        vehiculo.disponible = True
        db_session.commit()

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion/actualizar",
            json=payload_documentacion_valido(),
            headers=auth_headers(token),
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "No es posible actualizar la documentación del vehículo mientras esté disponible para alquilar"
        )

    def test_no_permite_actualizar_con_reserva_activa_devuelve_400(self, client, db_session):
        vehiculo, token = crear_vehiculo_base(db_session)
        vehiculo.estado_registro = "HABILITADO"
        vehiculo.disponible = False
        db_session.commit()

        # crear conductor y reserva activa
        conductor = crear_usuario(
            db=db_session,
            schema=RegistroUsuarioSchema(
                email="conductor.reserva@autospot.com",
                password="password123",
                rol="CLIENTE",
            ),
        )

        ahora = datetime.now(timezone.utc)
        reserva = Reserva(
            vehiculo_id=vehiculo.id,
            conductor_id=conductor.id,
            codigo="ABC123",
            estado="CONFIRMADA",
            monto_total=100.00,
            fecha_inicio=ahora,
            fecha_fin=ahora + timedelta(days=1),
            estacion_retiro="Palermo",
        )
        db_session.add(reserva)
        db_session.commit()

        response = client.patch(
            f"/vehiculos/{vehiculo.id}/documentacion/actualizar",
            json=payload_documentacion_valido(),
            headers=auth_headers(token),
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "No es posible actualizar la documentación del vehículo mientras haya una reserva activa en curso"
        )
