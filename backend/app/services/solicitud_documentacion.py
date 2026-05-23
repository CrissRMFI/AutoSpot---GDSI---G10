"""
Servicio de negocio — US 1R y 2R: Solicitudes de documentación pendientes.

Responsabilidades de esta capa:
    1. Consultar vehículos en estado EN_REVISION (documentación legal cargada
       pero aún no aprobada).
    2. Consultar documentación habilitante de conductores en estado
       PENDIENTE_VALIDACION.
    3. Unificar ambos conjuntos en una cola única.
    4. Ordenar la cola cronológicamente ascendente por fecha de solicitud,
       de manera que la atención sea equitativa según el orden de ingreso.

US 1R CA1 — retorna el conjunto de datos de los usuarios con documentación.
US 1R CA2 — devuelve lista vacía cuando no hay trámites pendientes.
US 2R CA1 — orden cronológico ascendente (más antiguo → más reciente).
US 2R CA2 — los nuevos ingresos quedan automáticamente al final.
"""
from sqlalchemy.orm import Session

from app.models.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductor,
)
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.solicitud_documentacion import (
    SolicitudDocumentacionSchema,
    TIPO_SOLICITUD_CONDUCTOR,
    TIPO_SOLICITUD_VEHICULO,
)


ESTADO_VEHICULO_EN_REVISION = "EN_REVISION"
ESTADO_CONDUCTOR_PENDIENTE = "PENDIENTE_VALIDACION"


def listar_solicitudes_pendientes(
    db: Session,
) -> list[SolicitudDocumentacionSchema]:
    """
    Lista todas las solicitudes de documentación pendientes de validación,
    unificando vehículos en EN_REVISION y documentación habilitante de
    conductores en PENDIENTE_VALIDACION.

    Returns:
        Lista de solicitudes ordenada cronológicamente ascendente (más antiguas
        primero). Si no hay trámites pendientes, retorna [].
    """
    solicitudes: list[SolicitudDocumentacionSchema] = []

    vehiculos_en_revision = (
        db.query(Vehiculo, Usuario)
        .join(Usuario, Vehiculo.propietario_id == Usuario.id)
        .filter(Vehiculo.estado_registro == ESTADO_VEHICULO_EN_REVISION)
        .all()
    )

    for vehiculo, propietario in vehiculos_en_revision:
        solicitudes.append(
            SolicitudDocumentacionSchema(
                tipo=TIPO_SOLICITUD_VEHICULO,
                recurso_id=vehiculo.id,
                usuario_id=propietario.id,
                usuario_email=propietario.email,
                estado=vehiculo.estado_registro,
                fecha_solicitud=vehiculo.updated_at,
                resumen=f"{vehiculo.marca} {vehiculo.modelo} ({vehiculo.anio})",
            )
        )

    conductores_pendientes = (
        db.query(DocumentacionHabilitanteConductor, Usuario)
        .join(Usuario, DocumentacionHabilitanteConductor.usuario_id == Usuario.id)
        .filter(
            DocumentacionHabilitanteConductor.estado_validacion
            == ESTADO_CONDUCTOR_PENDIENTE
        )
        .all()
    )

    for documentacion, conductor in conductores_pendientes:
        solicitudes.append(
            SolicitudDocumentacionSchema(
                tipo=TIPO_SOLICITUD_CONDUCTOR,
                recurso_id=documentacion.id,
                usuario_id=conductor.id,
                usuario_email=conductor.email,
                estado=documentacion.estado_validacion,
                fecha_solicitud=documentacion.updated_at,
                resumen=(
                    f"Licencia {documentacion.categoria} "
                    f"N° {documentacion.numero_licencia}"
                ),
            )
        )

    solicitudes.sort(key=lambda solicitud: solicitud.fecha_solicitud)

    return solicitudes
