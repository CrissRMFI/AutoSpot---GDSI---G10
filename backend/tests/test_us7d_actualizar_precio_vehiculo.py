"""
Tests Unitarios — US 7D: Actualización de precio del auto.

Historia de Usuario:
  Como dueño de un auto ya publicado,
  quiero poder modificar el precio diario de alquiler,
  para mantener mi tarifa actualizada según el mercado.

Diferencia con US 5D:
  US 5D cubre la definición inicial del precio (al publicar el vehículo).
  US 7D cubre la actualización de un precio ya existente.

Criterios de Aceptación cubiertos:
  ┌─────┬────────────────────────────────────────────────────────────────────┐
  │ CA  │ Descripción                                                        │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ CA1 │ Precio previo → el nuevo valor reemplaza al anterior              │
  │ CA2 │ Precio inválido → el sistema rechaza el cambio                    │
  │ CA3 │ Vehículo inexistente → el sistema informa que no existe           │
  └─────┴────────────────────────────────────────────────────────────────────┘
"""
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.exceptions import VehiculoNoEncontradoError
from app.schemas.usuario import RegistroUsuarioSchema
from app.schemas.vehiculo import (
    DefinirPrecioVehiculoSchema,
    FotoVehiculoSchema,
    RegistroVehiculoSchema,
)
from app.services.usuario import crear_usuario
from app.services.vehiculo import definir_precio_vehiculo, registrar_vehiculo


def _crear_propietario_con_vehiculo_y_precio(db_session):
    """
    Helper: crea un propietario, registra un vehículo y le asigna un precio inicial.
    Simula el estado al final de US 5D, punto de partida de US 7D.
    """
    propietario = crear_usuario(
        db=db_session,
        schema=RegistroUsuarioSchema(
            email="propietario.us7d@autospot.com",
            password="password123",
        ),
    )

    vehiculo = registrar_vehiculo(
        db=db_session,
        schema=RegistroVehiculoSchema(
            propietario_id=propietario.id,
            marca="Toyota",
            modelo="Etios",
            anio=2021,
            tipo_transmision="MANUAL",
            capacidad=5,
            categoria="SEDAN",
            tipo_combustible="NAFTA",
            pets_friendly=False,
            fotos=[
                FotoVehiculoSchema(
                    lado="FRENTE",
                    url="uploads/vehiculos/civic/frente.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="TRASERA",
                    url="uploads/vehiculos/civic/trasera.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_IZQUIERDO",
                    url="uploads/vehiculos/civic/lateral_izquierdo.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="LATERAL_DERECHO",
                    url="uploads/vehiculos/civic/lateral_derecho.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
                FotoVehiculoSchema(
                    lado="INTERIOR",
                    url="uploads/vehiculos/civic/interior.jpg",
                    formato="jpg",
                    tamanio_bytes=500_000,
                ),
            ],
        ),
    )

    definir_precio_vehiculo(
        db=db_session,
        vehiculo_id=vehiculo.id,
        precio_por_dia=Decimal("30000.00"),
    )

    return propietario, vehiculo


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 — Actualizar precio existente
#
#  "Dado que mi vehículo ya tiene un precio definido,
#   cuando ingreso un nuevo valor mayor a cero,
#   entonces el sistema reemplaza el precio anterior por el nuevo."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1_ActualizarPrecioExistente:
    """
    Verifica que el servicio sobreescribe el precio previo con el nuevo valor.
    """

    def test_actualiza_precio_de_vehiculo_ya_con_precio(self, db_session):
        """
        Dado un vehículo con precio_por_dia = 30000,
        cuando se llama al servicio con precio_por_dia = 50000,
        entonces el vehículo queda con precio_por_dia = 50000.
        """
        _, vehiculo = _crear_propietario_con_vehiculo_y_precio(db_session)

        vehiculo_actualizado = definir_precio_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            precio_por_dia=Decimal("50000.00"),
        )

        assert vehiculo_actualizado.id == vehiculo.id
        assert vehiculo_actualizado.precio_por_dia == Decimal("50000.00")

    def test_actualiza_precio_multiples_veces(self, db_session):
        """
        El precio puede modificarse más de una vez consecutivamente.
        Cada actualización reemplaza la anterior.
        """
        _, vehiculo = _crear_propietario_con_vehiculo_y_precio(db_session)

        definir_precio_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            precio_por_dia=Decimal("45000.00"),
        )

        vehiculo_final = definir_precio_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            precio_por_dia=Decimal("60000.00"),
        )

        assert vehiculo_final.precio_por_dia == Decimal("60000.00")


# ══════════════════════════════════════════════════════════════════════════════
#  CA2 — Precio de actualización inválido
#
#  "Dado que intento actualizar el precio,
#   cuando el nuevo valor es cero o negativo,
#   entonces el sistema rechaza el cambio."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA2_PrecioDeActualizacionInvalido:
    """
    Verifica que el schema rechaza precios de actualización inválidos.
    """

    @pytest.mark.parametrize("precio_invalido", [Decimal("0.00"), Decimal("-500.00")])
    def test_nuevo_precio_menor_o_igual_a_cero_es_invalido(self, precio_invalido):
        """
        El nuevo precio debe ser estrictamente mayor a cero.
        """
        with pytest.raises(ValidationError) as exc_info:
            DefinirPrecioVehiculoSchema(precio_por_dia=precio_invalido)

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any("Precio por dia invalido" in mensaje for mensaje in mensajes)


# ══════════════════════════════════════════════════════════════════════════════
#  CA3 — Vehículo inexistente
#
#  "Dado que intento actualizar el precio de un vehículo que no existe,
#   cuando confirmo la operación,
#   entonces el sistema informa que el vehículo no existe."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA3_VehiculoInexistenteActualizarPrecio:
    """
    Verifica que el servicio rechaza actualizaciones sobre vehículos inexistentes.
    """

    def test_no_actualiza_precio_si_vehiculo_no_existe(self, db_session):
        """
        Si vehiculo_id no corresponde a un vehículo persistido,
        el servicio debe lanzar VehiculoNoEncontradoError.
        """
        import uuid

        vehiculo_id_inexistente = uuid.uuid4()

        with pytest.raises(VehiculoNoEncontradoError) as exc_info:
            definir_precio_vehiculo(
                db=db_session,
                vehiculo_id=vehiculo_id_inexistente,
                precio_por_dia=Decimal("50000.00"),
            )

        assert str(exc_info.value) == "Vehiculo no encontrado"
