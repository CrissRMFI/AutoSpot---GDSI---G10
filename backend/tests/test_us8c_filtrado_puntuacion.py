"""
Tests unitarios — US 8C: Motor de filtrado de catálogo por puntuación.

Se prueba directamente el servicio `listar_vehiculos_disponibles`, que es la
lógica de negocio del filtro por puntuación.

Criterios de Aceptación cubiertos:
    CA 1 — Al pedir una puntuación, se devuelven solo los vehículos con esa
           puntuación o una mayor.
    CA 3 — Si ningún vehículo cumple, se devuelve una lista vacía.
    CA 4 — Sin filtro, se devuelve el catálogo completo.
"""
from decimal import Decimal

from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.services.vehiculo import listar_vehiculos_disponibles
from app.utils.security import hash_password


def _crear_propietario(db) -> Usuario:
    propietario = Usuario(
        email="prop-us8c@autospot.com",
        hashed_password=hash_password("password123"),
        rol="PROPIETARIO",
    )
    db.add(propietario)
    db.flush()
    return propietario


def _crear_vehiculo_disponible(
    db,
    propietario_id,
    calificacion_promedio,
    modelo: str = "Corolla",
) -> Vehiculo:
    """Crea un vehículo HABILITADO, disponible y con precio, listo para catálogo."""
    vehiculo = Vehiculo(
        propietario_id=propietario_id,
        marca="Toyota",
        modelo=modelo,
        anio=2020,
        tipo_transmision="AUTOMATICA",
        capacidad=5,
        categoria="SEDAN",
        tipo_combustible="NAFTA",
        pets_friendly=True,
        estado_registro="HABILITADO",
        disponible=True,
        precio_por_dia=Decimal("50000.00"),
        estacion="Estación Belgrano",
        calificacion_promedio=(
            Decimal(str(calificacion_promedio))
            if calificacion_promedio is not None
            else None
        ),
    )
    db.add(vehiculo)
    db.flush()
    return vehiculo


class TestCA4_SinFiltro:
    def test_sin_filtro_devuelve_catalogo_completo(self, db_session):
        """CA 4: sin puntuación, se devuelven todos los disponibles, incluso sin calificación."""
        propietario = _crear_propietario(db_session)
        _crear_vehiculo_disponible(db_session, propietario.id, None, "Corolla")
        _crear_vehiculo_disponible(db_session, propietario.id, 3.0, "Etios")
        _crear_vehiculo_disponible(db_session, propietario.id, 5.0, "Hilux")

        resultado = listar_vehiculos_disponibles(db_session)

        assert len(resultado) == 3


class TestCA1_FiltroPorPuntuacionMinima:
    def test_filtro_devuelve_solo_mayores_o_iguales(self, db_session):
        """CA 1: con puntuación 4, se devuelven solo los de 4 o más."""
        propietario = _crear_propietario(db_session)
        _crear_vehiculo_disponible(db_session, propietario.id, 2.0, "Corolla")
        _crear_vehiculo_disponible(db_session, propietario.id, 3.5, "Etios")
        v4 = _crear_vehiculo_disponible(db_session, propietario.id, 4.0, "Hilux")
        v45 = _crear_vehiculo_disponible(db_session, propietario.id, 4.5, "Fiesta")
        v5 = _crear_vehiculo_disponible(db_session, propietario.id, 5.0, "Focus")

        resultado = listar_vehiculos_disponibles(
            db_session, puntuacion_minima=Decimal("4")
        )

        ids = {v.id for v in resultado}
        assert ids == {v4.id, v45.id, v5.id}

    def test_filtro_excluye_vehiculos_sin_calificacion(self, db_session):
        """Un vehículo sin valoraciones (calificación None) no alcanza el filtro."""
        propietario = _crear_propietario(db_session)
        _crear_vehiculo_disponible(db_session, propietario.id, None, "Corolla")
        v5 = _crear_vehiculo_disponible(db_session, propietario.id, 5.0, "Hilux")

        resultado = listar_vehiculos_disponibles(
            db_session, puntuacion_minima=Decimal("3")
        )

        assert [v.id for v in resultado] == [v5.id]

    def test_filtro_incluye_el_borde_exacto(self, db_session):
        """El vehículo cuya calificación es exactamente la pedida se incluye."""
        propietario = _crear_propietario(db_session)
        v4 = _crear_vehiculo_disponible(db_session, propietario.id, 4.0, "Corolla")

        resultado = listar_vehiculos_disponibles(
            db_session, puntuacion_minima=Decimal("4")
        )

        assert [v.id for v in resultado] == [v4.id]


class TestCA3_SinCoincidencias:
    def test_filtro_sin_coincidencias_devuelve_lista_vacia(self, db_session):
        """CA 3: si ningún vehículo cumple, se devuelve lista vacía."""
        propietario = _crear_propietario(db_session)
        _crear_vehiculo_disponible(db_session, propietario.id, 2.0, "Corolla")
        _crear_vehiculo_disponible(db_session, propietario.id, 3.0, "Etios")

        resultado = listar_vehiculos_disponibles(
            db_session, puntuacion_minima=Decimal("4.5")
        )

        assert resultado == []
