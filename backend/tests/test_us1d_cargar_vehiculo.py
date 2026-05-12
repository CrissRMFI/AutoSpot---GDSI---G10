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
  │ CA1 │ Campos obligatorios omitidos → bloquea guardado                  │
│ CA6 │ Campos obligatorios correctos → información del auto guardada    │
  └─────┴──────────────────────────────────────────────────────────────────┘

"""
import pytest
from pydantic import ValidationError

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


# ══════════════════════════════════════════════════════════════════════════════
#  CA1 — Campos obligatorios omitidos
#
#  "Dado que soy dueño de un auto y me encuentro llenando el formulario,
#   cuando falten campos obligatorios, entonces se bloquea el guardado."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA1_CamposObligatoriosVehiculo:
    """
    Verifica que el schema rechaza payloads incompletos o inválidos
    antes de llegar al servicio de negocio.
    """

    PAYLOAD_VALIDO = {
        "propietario_id": "00000000-0000-0000-0000-000000000001",
        "marca": "Toyota",
        "modelo": "Corolla",
        "anio": 2020,
        "tipo_transmision": "AUTOMATICA",
        "capacidad": 5,
        "categoria": "SEDAN",
        "tipo_combustible": "NAFTA",
        "pets_friendly": True,
        "fotos": [
            {
                "lado": "FRENTE",
                "url": "uploads/vehiculos/corolla/frente.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "TRASERA",
                "url": "uploads/vehiculos/corolla/trasera.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "LATERAL_IZQUIERDO",
                "url": "uploads/vehiculos/corolla/lateral_izquierdo.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "LATERAL_DERECHO",
                "url": "uploads/vehiculos/corolla/lateral_derecho.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
        ],
    }

    def _assert_error_validacion(self, payload: dict, campo: str) -> None:
        """
        Helper: verifica que Pydantic rechaza el payload y marca el campo.
        """
        with pytest.raises(ValidationError) as exc_info:
            RegistroVehiculoSchema(**payload)

        errores = exc_info.value.errors()
        campos_con_error = [error["loc"][0] for error in errores]

        assert campo in campos_con_error, (
            f"Se esperaba error en campo '{campo}', "
            f"pero los errores fueron: {errores}"
        )

    def _assert_error_campo_obligatorio(self, payload: dict) -> None:
        """
        Helper: verifica que se informa el mensaje canónico de campo obligatorio.
        """
        with pytest.raises(ValidationError) as exc_info:
            RegistroVehiculoSchema(**payload)

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]

        assert any("Campo obligatorio" in mensaje for mensaje in mensajes), (
            f"Se esperaba 'Campo obligatorio', pero se recibió: {mensajes}"
        )

    def test_ca1_marca_vacia_es_invalida(self):
        """La marca es obligatoria."""
        payload = {**self.PAYLOAD_VALIDO, "marca": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca1_modelo_vacio_es_invalido(self):
        """El modelo es obligatorio."""
        payload = {**self.PAYLOAD_VALIDO, "modelo": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca1_tipo_transmision_vacio_es_invalido(self):
        """El tipo de transmisión es obligatorio."""
        payload = {**self.PAYLOAD_VALIDO, "tipo_transmision": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca1_categoria_vacia_es_invalida(self):
        """La categoría es obligatoria."""
        payload = {**self.PAYLOAD_VALIDO, "categoria": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca1_tipo_combustible_vacio_es_invalido(self):
        """El tipo de combustible es obligatorio."""
        payload = {**self.PAYLOAD_VALIDO, "tipo_combustible": ""}
        self._assert_error_campo_obligatorio(payload)

    def test_ca1_capacidad_invalida_bloquea_guardado(self):
        """La capacidad debe ser mayor a cero."""
        payload = {**self.PAYLOAD_VALIDO, "capacidad": 0}

        with pytest.raises(ValidationError) as exc_info:
            RegistroVehiculoSchema(**payload)

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any("Capacidad invalida" in mensaje for mensaje in mensajes)

    def test_ca1_fotos_vacias_bloquean_guardado(self):
        """Debe enviarse la cantidad mínima de fotos requeridas."""
        payload = {**self.PAYLOAD_VALIDO, "fotos": []}

        with pytest.raises(ValidationError) as exc_info:
            RegistroVehiculoSchema(**payload)

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any(
            "Cantidad minima de fotos requerida" in mensaje
            for mensaje in mensajes
        )

    def test_ca1_campo_obligatorio_omitido_bloquea_guardado(self):
        """Si se omite un campo obligatorio, Pydantic debe rechazar el payload."""
        payload = self.PAYLOAD_VALIDO.copy()
        payload.pop("marca")

        self._assert_error_validacion(payload, "marca")


# ══════════════════════════════════════════════════════════════════════════════
#  CA2 — Año del auto inválido
#
#  "Dado que soy dueño de un auto y me encuentro llenando el formulario,
#   cuando ingreso un año mayor al actual o menor al límite permitido,
#   entonces se informa el error correspondiente."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA2_AnioVehiculo:
    """
    Verifica que el schema rechaza años fuera del rango permitido.
    """

    PAYLOAD_VALIDO = TestCA1_CamposObligatoriosVehiculo.PAYLOAD_VALIDO

    def _assert_error_anio_invalido(self, anio: int) -> None:
        """Helper: verifica que el año inválido sea rechazado."""
        payload = {**self.PAYLOAD_VALIDO, "anio": anio}

        with pytest.raises(ValidationError) as exc_info:
            RegistroVehiculoSchema(**payload)

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any("Anio del auto invalido" in mensaje for mensaje in mensajes), (
            f"Se esperaba 'Anio del auto invalido', pero se recibió: {mensajes}"
        )

    def test_ca2_anio_mayor_al_actual_es_invalido(self):
        """Un año posterior al actual no debe ser aceptado."""
        from datetime import datetime

        anio_futuro = datetime.now().year + 1
        self._assert_error_anio_invalido(anio_futuro)

    def test_ca2_anio_menor_al_limite_permitido_es_invalido(self):
        """Un año menor a 1990 no debe ser aceptado."""
        self._assert_error_anio_invalido(1989)

    def test_ca2_anio_limite_permitido_es_valido(self):
        """El año mínimo permitido debe ser aceptado."""
        payload = {**self.PAYLOAD_VALIDO, "anio": 1990}

        schema = RegistroVehiculoSchema(**payload)

        assert schema.anio == 1990

    def test_ca2_anio_actual_es_valido(self):
        """El año actual debe ser aceptado."""
        from datetime import datetime

        anio_actual = datetime.now().year
        payload = {**self.PAYLOAD_VALIDO, "anio": anio_actual}

        schema = RegistroVehiculoSchema(**payload)

        assert schema.anio == anio_actual


# ══════════════════════════════════════════════════════════════════════════════
#  CA3 — Foto con formato inválido o tamaño mayor al permitido
#
#  "Dado que soy dueño de un auto y me encuentro cargando fotos,
#   cuando cargo una foto en un formato inválido o de mayor tamaño al permitido,
#   entonces se rechaza la foto y se informa el error correspondiente."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA3_FotosVehiculo:
    """
    Verifica que el schema rechaza fotos con formato inválido, tamaño inválido
    o tamaño superior al permitido.
    """

    def test_ca3_formato_de_foto_invalido_es_rechazado(self):
        """Una foto con formato no permitido debe ser rechazada."""
        with pytest.raises(ValidationError) as exc_info:
            FotoVehiculoSchema(
                lado="FRENTE",
                url="uploads/vehiculos/corolla/frente.gif",
                formato="gif",
                tamanio_bytes=500_000,
            )

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any("Formato de foto invalido" in mensaje for mensaje in mensajes), (
            f"Se esperaba 'Formato de foto invalido', pero se recibió: {mensajes}"
        )

    def test_ca3_tamanio_de_foto_mayor_al_permitido_es_rechazado(self):
        """Una foto que supera los 5MB debe ser rechazada."""
        tamanio_mayor_a_5mb = (5 * 1024 * 1024) + 1

        with pytest.raises(ValidationError) as exc_info:
            FotoVehiculoSchema(
                lado="FRENTE",
                url="uploads/vehiculos/corolla/frente.jpg",
                formato="jpg",
                tamanio_bytes=tamanio_mayor_a_5mb,
            )

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any("Tamanio de foto excedido" in mensaje for mensaje in mensajes), (
            f"Se esperaba 'Tamanio de foto excedido', pero se recibió: {mensajes}"
        )

    def test_ca3_tamanio_de_foto_cero_es_rechazado(self):
        """Una foto con tamaño cero no debe ser aceptada."""
        with pytest.raises(ValidationError) as exc_info:
            FotoVehiculoSchema(
                lado="FRENTE",
                url="uploads/vehiculos/corolla/frente.jpg",
                formato="jpg",
                tamanio_bytes=0,
            )

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any("Tamanio de foto invalido" in mensaje for mensaje in mensajes), (
            f"Se esperaba 'Tamanio de foto invalido', pero se recibió: {mensajes}"
        )

    def test_ca3_formato_jpg_es_valido(self):
        """El formato jpg debe ser aceptado."""
        foto = FotoVehiculoSchema(
            lado="FRENTE",
            url="uploads/vehiculos/corolla/frente.jpg",
            formato="jpg",
            tamanio_bytes=500_000,
        )

        assert foto.formato == "jpg"

    def test_ca3_formato_png_es_valido(self):
        """El formato png debe ser aceptado."""
        foto = FotoVehiculoSchema(
            lado="FRENTE",
            url="uploads/vehiculos/corolla/frente.png",
            formato="png",
            tamanio_bytes=500_000,
        )

        assert foto.formato == "png"

    def test_ca3_formato_webp_es_valido(self):
        """El formato webp debe ser aceptado."""
        foto = FotoVehiculoSchema(
            lado="FRENTE",
            url="uploads/vehiculos/corolla/frente.webp",
            formato="webp",
            tamanio_bytes=500_000,
        )

        assert foto.formato == "webp"


# ══════════════════════════════════════════════════════════════════════════════
#  CA5 — Cantidad mínima de fotos requeridas
#
#  "Dado que soy dueño de un auto y me encuentro cargando fotos,
#   cuando no cargo la cantidad mínima de fotos requeridas, que en este caso
#   son 4, una de cada lado del auto, entonces se bloquea la solicitud."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA5_FotosMinimasVehiculo:
    """
    Verifica que el registro del vehículo exija cuatro fotos mínimas,
    una por cada lado requerido.
    """

    PAYLOAD_VALIDO = TestCA1_CamposObligatoriosVehiculo.PAYLOAD_VALIDO

    def _assert_error_fotos_requeridas(self, fotos: list[dict]) -> None:
        """Helper: verifica que el schema rechaza el conjunto de fotos."""
        payload = {**self.PAYLOAD_VALIDO, "fotos": fotos}

        with pytest.raises(ValidationError) as exc_info:
            RegistroVehiculoSchema(**payload)

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any(
            "Cantidad minima de fotos requerida" in mensaje
            for mensaje in mensajes
        ), f"Se esperaba error de fotos requeridas, pero se recibió: {mensajes}"

    def test_ca5_menos_de_cuatro_fotos_bloquea_solicitud(self):
        """Con solo tres fotos, la solicitud debe bloquearse."""
        fotos = [
            {
                "lado": "FRENTE",
                "url": "uploads/vehiculos/corolla/frente.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "TRASERA",
                "url": "uploads/vehiculos/corolla/trasera.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "LATERAL_IZQUIERDO",
                "url": "uploads/vehiculos/corolla/lateral_izquierdo.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
        ]

        self._assert_error_fotos_requeridas(fotos)

    def test_ca5_cuatro_fotos_pero_falta_un_lado_requerido_bloquea_solicitud(self):
        """
        Aunque haya cuatro fotos, si falta un lado requerido, debe fallar.
        En este caso falta LATERAL_DERECHO y se repite FRENTE.
        """
        fotos = [
            {
                "lado": "FRENTE",
                "url": "uploads/vehiculos/corolla/frente_1.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "FRENTE",
                "url": "uploads/vehiculos/corolla/frente_2.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "TRASERA",
                "url": "uploads/vehiculos/corolla/trasera.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
            {
                "lado": "LATERAL_IZQUIERDO",
                "url": "uploads/vehiculos/corolla/lateral_izquierdo.jpg",
                "formato": "jpg",
                "tamanio_bytes": 500_000,
            },
        ]

        self._assert_error_fotos_requeridas(fotos)

    def test_ca5_cuatro_fotos_una_de_cada_lado_es_valido(self):
        """Con cuatro fotos y una de cada lado requerido, el schema es válido."""
        schema = RegistroVehiculoSchema(**self.PAYLOAD_VALIDO)

        lados = {foto.lado for foto in schema.fotos}

        assert len(schema.fotos) == 4
        assert lados == {
            "FRENTE",
            "TRASERA",
            "LATERAL_IZQUIERDO",
            "LATERAL_DERECHO",
        }


# ══════════════════════════════════════════════════════════════════════════════
#  CA4 — Combinación marca/modelo inexistente
#
#  "Dado que soy dueño de un auto y me encuentro llenando el formulario,
#   cuando la combinación marca + modelo no exista, entonces se impide continuar."
# ══════════════════════════════════════════════════════════════════════════════
class TestCA4_MarcaModeloVehiculo:
    """
    Verifica que el schema acepte únicamente combinaciones marca/modelo
    existentes en el catálogo inicial hardcodeado.
    """

    PAYLOAD_VALIDO = TestCA1_CamposObligatoriosVehiculo.PAYLOAD_VALIDO

    def _assert_error_marca_modelo(self, marca: str, modelo: str) -> None:
        """Helper: verifica que la combinación marca/modelo sea rechazada."""
        payload = {
            **self.PAYLOAD_VALIDO,
            "marca": marca,
            "modelo": modelo,
        }

        with pytest.raises(ValidationError) as exc_info:
            RegistroVehiculoSchema(**payload)

        mensajes = [error.get("msg", "") for error in exc_info.value.errors()]
        assert any(
            "Combinacion marca modelo inexistente" in mensaje
            for mensaje in mensajes
        ), (
            "Se esperaba 'Combinacion marca modelo inexistente', "
            f"pero se recibió: {mensajes}"
        )

    def test_ca4_marca_modelo_existente_es_valida(self):
        """Toyota Corolla existe en el catálogo inicial."""
        payload = {
            **self.PAYLOAD_VALIDO,
            "marca": "Toyota",
            "modelo": "Corolla",
        }

        schema = RegistroVehiculoSchema(**payload)

        assert schema.marca == "Toyota"
        assert schema.modelo == "Corolla"

    def test_ca4_marca_inexistente_bloquea_solicitud(self):
        """Una marca inexistente debe impedir continuar."""
        self._assert_error_marca_modelo(
            marca="MarcaInexistente",
            modelo="Corolla",
        )

    def test_ca4_modelo_inexistente_para_marca_existente_bloquea_solicitud(self):
        """Un modelo que no pertenece a la marca debe impedir continuar."""
        self._assert_error_marca_modelo(
            marca="Toyota",
            modelo="Fiesta",
        )

    def test_ca4_modelo_inexistente_bloquea_solicitud(self):
        """Un modelo inexistente para una marca válida debe impedir continuar."""
        self._assert_error_marca_modelo(
            marca="Toyota",
            modelo="ModeloFantasma",
        )

