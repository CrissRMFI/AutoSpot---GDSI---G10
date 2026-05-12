"""
Tests Unitarios — US 1D: Cargar características y fotos del auto.

Historia de Usuario:
  Como dueño de auto,
  quiero agregar las características detalladas y subir fotos de mi auto,
  para el registro del auto en la plataforma.

Criterios de Aceptación cubiertos inicialmente:
  ┌─────┬──────────────────────────────────────────────────────────────────┐
  │ CA  │ Descripción                                                      │
  ├─────┼──────────────────────────────────────────────────────────────────┤
  │ CA6 │ Campos obligatorios correctos → información del auto guardada    │
  └─────┴──────────────────────────────────────────────────────────────────┘

Pendientes:
  CA1 │ Campos obligatorios omitidos → bloquea guardado.
  CA2 │ Año mayor al actual o menor al límite permitido → error.
  CA3 │ Foto con formato inválido o tamaño mayor al permitido → error.
  CA4 │ Combinación marca/modelo inexistente → impide continuar.
  CA5 │ Menos de 4 fotos, una de cada lado → bloquea solicitud.
"""
from app.schemas.usuario import RegistroUsuarioSchema
from app.schemas.vehiculo import FotoVehiculoSchema, RegistroVehiculoSchema
from app.services.usuario import crear_usuario
from app.services.vehiculo import registrar_vehiculo


# ══════════════════════════════════════════════════════════════════════════════
#  CA6 — Registro exitoso del auto
#
#  "Dado que completé todos los campos obligatorios correctamente,
#   cuando hago clic en guardar, entonces la información del auto se guarda
#   exitosamente."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA6_RegistroExitosoVehiculo:
    """
    Verifica el happy path de registro de un vehículo a nivel servicio.
    """

    def test_registra_vehiculo_con_caracteristicas_y_fotos_validas(self, db_session):
        """
        El servicio debe registrar las características obligatorias del vehículo
        y asociar las fotos requeridas al propietario.
        """
        propietario = crear_usuario(
            db=db_session,
            schema=RegistroUsuarioSchema(
                email="propietario.vehiculo@autospot.com",
                password="password123",
            ),
        )

        payload = RegistroVehiculoSchema(
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
            ],
        )

        vehiculo = registrar_vehiculo(db=db_session, schema=payload)

        assert vehiculo.id is not None
        assert vehiculo.propietario_id == propietario.id
        assert vehiculo.marca == "Toyota"
        assert vehiculo.modelo == "Corolla"
        assert vehiculo.anio == 2020
        assert vehiculo.tipo_transmision == "AUTOMATICA"
        assert vehiculo.capacidad == 5
        assert vehiculo.categoria == "SEDAN"
        assert vehiculo.tipo_combustible == "NAFTA"
        assert vehiculo.pets_friendly is True
        assert vehiculo.estado_registro == "PENDIENTE_DOCUMENTACION"

        assert len(vehiculo.fotos) == 4
        lados = {foto.lado for foto in vehiculo.fotos}
        assert lados == {
            "FRENTE",
            "TRASERA",
            "LATERAL_IZQUIERDO",
            "LATERAL_DERECHO",
        }
