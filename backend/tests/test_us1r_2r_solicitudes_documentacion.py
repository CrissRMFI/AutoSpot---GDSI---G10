"""
Tests Unitarios — US 1R y 2R: Solicitudes de documentación pendientes.

Criterios de Aceptación cubiertos a nivel servicio:
  ┌──────┬─────────────────────────────────────────────────────────────────┐
  │ CA   │ Descripción                                                     │
  ├──────┼─────────────────────────────────────────────────────────────────┤
  │ 1R-1 │ Existen perfiles con documentación → retorna conjunto de datos  │
  │ 1R-2 │ No hay trámites pendientes → retorna lista vacía                │
  │ 2R-1 │ Múltiples solicitudes → orden cronológico ascendente            │
  │ 2R-2 │ Ingreso nuevo → queda al final de la cola                       │
  └──────┴─────────────────────────────────────────────────────────────────┘
"""
import uuid
from datetime import date, datetime, timezone, timedelta

from app.models.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductor,
)
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.solicitud_documentacion import (
    TIPO_SOLICITUD_CONDUCTOR,
    TIPO_SOLICITUD_VEHICULO,
)
from app.services.solicitud_documentacion import listar_solicitudes_pendientes


def _crear_usuario(db_session, email: str, rol: str = "CLIENTE") -> Usuario:
    usuario = Usuario(
        email=email,
        hashed_password="x" * 60,
        rol=rol,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


def _crear_vehiculo_en_revision(
    db_session,
    propietario_id,
    fecha_solicitud: datetime,
    marca: str = "Toyota",
    modelo: str = "Corolla",
) -> Vehiculo:
    vehiculo = Vehiculo(
        propietario_id=propietario_id,
        marca=marca,
        modelo=modelo,
        anio=2020,
        tipo_transmision="AUTOMATICA",
        capacidad=5,
        categoria="SEDAN",
        tipo_combustible="NAFTA",
        pets_friendly=True,
        estado_registro="EN_REVISION",
        created_at=fecha_solicitud,
        updated_at=fecha_solicitud,
    )
    db_session.add(vehiculo)
    db_session.commit()
    db_session.refresh(vehiculo)
    return vehiculo


def _crear_doc_habilitante_pendiente(
    db_session,
    usuario_id,
    fecha_solicitud: datetime,
) -> DocumentacionHabilitanteConductor:
    documentacion = DocumentacionHabilitanteConductor(
        usuario_id=usuario_id,
        categoria="B1",
        fecha_emision=date(2024, 1, 1),
        fecha_vencimiento=date(2029, 1, 1),
        foto_licencia_frente_url="uploads/frente.jpg",
        foto_licencia_dorso_url="uploads/dorso.jpg",
        estado_validacion="PENDIENTE_REVISION",
        created_at=fecha_solicitud,
        updated_at=fecha_solicitud,
    )
    db_session.add(documentacion)
    db_session.commit()
    db_session.refresh(documentacion)
    return documentacion


# ══════════════════════════════════════════════════════════════════════════════
#  US 1R CA1 — Retorna el conjunto de datos cuando hay solicitudes
# ══════════════════════════════════════════════════════════════════════════════
class TestUS1R_CA1_RetornaSolicitudes:
    def test_lista_vehiculos_en_revision(self, db_session):
        propietario = _crear_usuario(db_session, "propietario@autospot.com")
        ahora = datetime.now(timezone.utc)
        vehiculo = _crear_vehiculo_en_revision(
            db_session, propietario.id, ahora,
        )

        solicitudes = listar_solicitudes_pendientes(db=db_session)

        assert len(solicitudes) == 1
        solicitud = solicitudes[0]
        assert solicitud.tipo == TIPO_SOLICITUD_VEHICULO
        assert solicitud.recurso_id == vehiculo.id
        assert solicitud.usuario_id == propietario.id
        assert solicitud.usuario_email == "propietario@autospot.com"
        assert solicitud.estado == "EN_REVISION"

    def test_lista_documentacion_habilitante_pendiente(self, db_session):
        conductor = _crear_usuario(db_session, "conductor@autospot.com")
        ahora = datetime.now(timezone.utc)
        documentacion = _crear_doc_habilitante_pendiente(
            db_session, conductor.id, ahora,
        )

        solicitudes = listar_solicitudes_pendientes(db=db_session)

        assert len(solicitudes) == 1
        solicitud = solicitudes[0]
        assert solicitud.tipo == TIPO_SOLICITUD_CONDUCTOR
        assert solicitud.recurso_id == documentacion.id
        assert solicitud.usuario_id == conductor.id
        assert solicitud.usuario_email == "conductor@autospot.com"
        assert solicitud.estado == "PENDIENTE_REVISION"

    def test_lista_combina_vehiculos_y_conductores(self, db_session):
        propietario = _crear_usuario(db_session, "propietario@autospot.com")
        conductor = _crear_usuario(db_session, "conductor@autospot.com")
        ahora = datetime.now(timezone.utc)

        _crear_vehiculo_en_revision(db_session, propietario.id, ahora)
        _crear_doc_habilitante_pendiente(db_session, conductor.id, ahora)

        solicitudes = listar_solicitudes_pendientes(db=db_session)

        tipos = {solicitud.tipo for solicitud in solicitudes}
        assert tipos == {TIPO_SOLICITUD_VEHICULO, TIPO_SOLICITUD_CONDUCTOR}
        assert len(solicitudes) == 2


# ══════════════════════════════════════════════════════════════════════════════
#  US 1R CA2 — Lista vacía cuando no hay trámites pendientes
# ══════════════════════════════════════════════════════════════════════════════
class TestUS1R_CA2_ListaVacia:
    def test_sin_solicitudes_devuelve_lista_vacia(self, db_session):
        solicitudes = listar_solicitudes_pendientes(db=db_session)
        assert solicitudes == []

    def test_vehiculo_habilitado_no_aparece_en_la_cola(self, db_session):
        propietario = _crear_usuario(db_session, "propietario@autospot.com")
        ahora = datetime.now(timezone.utc)
        vehiculo = _crear_vehiculo_en_revision(db_session, propietario.id, ahora)
        vehiculo.estado_registro = "HABILITADO"
        db_session.commit()

        solicitudes = listar_solicitudes_pendientes(db=db_session)
        assert solicitudes == []

    def test_conductor_validado_no_aparece_en_la_cola(self, db_session):
        conductor = _crear_usuario(db_session, "conductor@autospot.com")
        ahora = datetime.now(timezone.utc)
        documentacion = _crear_doc_habilitante_pendiente(
            db_session, conductor.id, ahora,
        )
        documentacion.estado_validacion = "APROBADO"
        db_session.commit()

        solicitudes = listar_solicitudes_pendientes(db=db_session)
        assert solicitudes == []


# ══════════════════════════════════════════════════════════════════════════════
#  US 2R CA1 — Orden cronológico ascendente
# ══════════════════════════════════════════════════════════════════════════════
class TestUS2R_CA1_OrdenCronologico:
    def test_orden_ascendente_entre_vehiculos(self, db_session):
        propietario = _crear_usuario(db_session, "propietario@autospot.com")
        ayer = datetime.now(timezone.utc) - timedelta(days=1)
        hace_una_hora = datetime.now(timezone.utc) - timedelta(hours=1)

        vehiculo_reciente = _crear_vehiculo_en_revision(
            db_session, propietario.id, hace_una_hora, modelo="Etios",
        )
        vehiculo_antiguo = _crear_vehiculo_en_revision(
            db_session, propietario.id, ayer, modelo="Corolla",
        )

        solicitudes = listar_solicitudes_pendientes(db=db_session)

        assert [s.recurso_id for s in solicitudes] == [
            vehiculo_antiguo.id,
            vehiculo_reciente.id,
        ]

    def test_orden_ascendente_mezclando_vehiculos_y_conductores(self, db_session):
        propietario = _crear_usuario(db_session, "propietario@autospot.com")
        conductor = _crear_usuario(db_session, "conductor@autospot.com")

        t0 = datetime.now(timezone.utc) - timedelta(days=3)
        t1 = datetime.now(timezone.utc) - timedelta(days=2)
        t2 = datetime.now(timezone.utc) - timedelta(days=1)

        documentacion_mas_antigua = _crear_doc_habilitante_pendiente(
            db_session, conductor.id, t0,
        )
        vehiculo_intermedio = _crear_vehiculo_en_revision(
            db_session, propietario.id, t1,
        )
        # Solicitud más reciente
        propietario_2 = _crear_usuario(db_session, "propietario2@autospot.com")
        vehiculo_reciente = _crear_vehiculo_en_revision(
            db_session, propietario_2.id, t2, modelo="Hilux",
        )

        solicitudes = listar_solicitudes_pendientes(db=db_session)

        assert [s.recurso_id for s in solicitudes] == [
            documentacion_mas_antigua.id,
            vehiculo_intermedio.id,
            vehiculo_reciente.id,
        ]


# ══════════════════════════════════════════════════════════════════════════════
#  US 2R CA2 — Nuevos ingresos quedan al final
# ══════════════════════════════════════════════════════════════════════════════
class TestUS2R_CA2_NuevoIngresoAlFinal:
    def test_nuevo_ingreso_va_al_final(self, db_session):
        propietario_viejo = _crear_usuario(db_session, "viejo@autospot.com")
        propietario_nuevo = _crear_usuario(db_session, "nuevo@autospot.com")

        hace_una_semana = datetime.now(timezone.utc) - timedelta(days=7)
        vehiculo_existente = _crear_vehiculo_en_revision(
            db_session, propietario_viejo.id, hace_una_semana,
        )

        # Llega un trámite nuevo recién ahora.
        ahora = datetime.now(timezone.utc)
        vehiculo_nuevo = _crear_vehiculo_en_revision(
            db_session, propietario_nuevo.id, ahora, modelo="Hilux",
        )

        solicitudes = listar_solicitudes_pendientes(db=db_session)

        assert solicitudes[0].recurso_id == vehiculo_existente.id
        assert solicitudes[-1].recurso_id == vehiculo_nuevo.id
