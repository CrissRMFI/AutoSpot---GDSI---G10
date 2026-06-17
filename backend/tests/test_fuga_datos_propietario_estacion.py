import uuid
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

def _ids(data) -> set:
    return {v["id"] for v in data}

class TestFugaDatosPropietarioCatalogo:
    def test_propietario_solo_ve_sus_autos_en_catalogo(self):
        """
        Reproduce el escenario de fuga de datos en la vista de estaciones del panel
        del propietario. Al llamar al catálogo (que es usado para alimentar el mapa
        de estaciones), un PROPIETARIO solo debe recibir sus propios autos, 
        mientras que un CLIENTE debe recibirlos todos.
        """
        engine, client_context = _crear_cliente()
        try:
            with client_context as client:
                # 1. Crear Dueño A y Dueño B, registrar y habilitar vehículos para ambos
                # _registrar_vehiculo crea el propietario implícitamente
                vehiculo_a, token_a = _registrar_vehiculo(client, "duenio_a@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo_a["id"])
                
                vehiculo_b, token_b = _registrar_vehiculo(client, "duenio_b@autospot.com")
                _hacer_vehiculo_reservable(engine, vehiculo_b["id"])

                # 2. El Dueño A hace la petición GET al endpoint de catálogo
                response = client.get(
                    "/vehiculos/catalogo",
                    headers=_auth_headers(token_a),
                )

                assert response.status_code == 200, response.text
                ids = _ids(response.json())
                
                # 3. Validar: El test hace assert de que SÓLO aparece el Auto del Dueño A.
                assert vehiculo_a["id"] in ids, "El auto del Dueño A debería estar visible para el Dueño A"
                assert vehiculo_b["id"] not in ids, "El auto del Dueño B NO debería estar visible para el Dueño A"
                
                # 4. Validar comportamiento para Cliente (debe ver ambos)
                _, token_cliente = _registrar_y_loguear_usuario(
                    client, "cliente@autospot.com", rol="CLIENTE"
                )
                response_cli = client.get(
                    "/vehiculos/catalogo",
                    headers=_auth_headers(token_cliente),
                )
                assert response_cli.status_code == 200, response_cli.text
                ids_cli = _ids(response_cli.json())
                
                assert vehiculo_a["id"] in ids_cli, "El cliente debería ver el auto de A"
                assert vehiculo_b["id"] in ids_cli, "El cliente debería ver el auto de B"
                
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(engine)
            engine.dispose()
