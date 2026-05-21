"""
Tests Unitarios — US 5D: Definir precio del auto.

Historia de Usuario:
  Como dueño de un auto recién registrado y habilitado,
  quiero establecer el valor de la tarifa de alquiler por día,
  para que mi auto pueda empezar a generar ingresos.

Alcance de esta iteración:
  - solo precio por día
  - sin descuentos
  - sin comisión
  - sin precio dinámico
  - sin moneda múltiple
  - sin precio semanal/mensual

Criterios de Aceptación cubiertos inicialmente:
  ┌─────┬──────────────────────────────────────────────────────────────────┐
  │ CA  │ Descripción                                                      │
  ├─────┼──────────────────────────────────────────────────────────────────┤
  │ CA1 │ Precio mayor a cero → permite guardar tarifa diaria              │
  └─────┴──────────────────────────────────────────────────────────────────┘
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
from app.services.vehiculo import registrar_vehiculo, definir_precio_vehiculo


def _crear_propietario_con_vehiculo(db_session):
    """
    Helper: crea un Usuario propietario y registra un vehículo válido.

    Se reutiliza el flujo real de US5U + US1D para que la US5D opere
    sobre datos consistentes del dominio.
    """
    propietario = crear_usuario(
        db=db_session,
        schema=RegistroUsuarioSchema(
            email="propietario.us5d@autospot.com",
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

    return propietario, vehiculo


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 — Definir precio válido
#
#  "Dado que estoy configurando la tarifa,
#   cuando ingreso un valor mayor a cero,
#   entonces el sistema guarda la tarifa diaria del auto."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1_DefinirPrecioVehiculo:
    """
    Verifica el happy path de definición de tarifa diaria a nivel servicio.
    """

    def test_define_precio_por_dia_valido_en_vehiculo_existente(self, db_session):
        """
        El servicio debe guardar el precio por día sobre un vehículo existente.
        """
        _, vehiculo = _crear_propietario_con_vehiculo(db_session)

        vehiculo_actualizado = definir_precio_vehiculo(
            db=db_session,
            vehiculo_id=vehiculo.id,
            precio_por_dia=Decimal("35000.00"),
        )

        assert vehiculo_actualizado.id == vehiculo.id
        assert vehiculo_actualizado.precio_por_dia == Decimal("35000.00")


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 — Precio inválido
#
#  "Dado que estoy configurando la tarifa,
#   cuando ingreso cero o un número negativo,
#   entonces el sistema impide guardar el precio."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1_PrecioInvalidoVehiculo:
    """
    Verifica que el schema rechaza tarifas diarias iguales o menores a cero.
    """

    @pytest.mark.parametrize("precio_invalido", [Decimal("0.00"), Decimal("-1.00")])
    def test_precio_por_dia_menor_o_igual_a_cero_es_invalido(
        self,
        precio_invalido,
    ):
        """
        El precio por día debe ser estrictamente mayor a cero.
        """
        with pytest.raises(ValidationError) as exc_info:
            DefinirPrecioVehiculoSchema(precio_por_dia=precio_invalido)

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]

        assert any("Precio por dia invalido" in mensaje for mensaje in mensajes)


# ══════════════════════════════════════════════════════════════════════════════
#  Vehículo inexistente
#
#  "Dado que intento definir precio para un vehículo inexistente,
#   cuando confirmo la operación,
#   entonces el sistema informa que el vehículo no existe."
# ══════════════════════════════════════════════════════════════════════════════
class TestVehiculoInexistenteDefinirPrecio:
    """
    Verifica que el servicio no permita definir precio para vehículos inexistentes.
    """

    def test_no_define_precio_si_vehiculo_no_existe(self, db_session):
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
                precio_por_dia=Decimal("35000.00"),
            )

        assert str(exc_info.value) == "Vehiculo no encontrado"
