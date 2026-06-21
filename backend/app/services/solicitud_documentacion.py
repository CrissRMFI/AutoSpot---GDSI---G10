"""
Servicio de negocio — US 1R y 2R: Solicitudes de documentación pendientes.

Responsabilidades de esta capa:
    1. Consultar vehículos en estado EN_REVISION (documentación legal cargada
       pero aún no aprobada).
    2. Consultar documentación habilitante de conductores en estado
       PENDIENTE_REVISION.
    3. Unificar ambos conjuntos en una cola única.
    4. Ordenar la cola cronológicamente ascendente por fecha de solicitud,
       de manera que la atención sea equitativa según el orden de ingreso.

US 1R CA1 — retorna el conjunto de datos de los usuarios con documentación.
US 1R CA2 — devuelve lista vacía cuando no hay trámites pendientes.
US 2R CA1 — orden cronológico ascendente (más antiguo → más reciente).
US 2R CA2 — los nuevos ingresos quedan automáticamente al final.
"""
from sqlalchemy.orm import Session

from app.exceptions import (
    SolicitudDocumentacionNoEncontradaError,
    TipoSolicitudDocumentacionInvalidoError,
)
from app.models.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductor,
    EstadoHabilitacion,
)
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.solicitud_documentacion import (
    DocumentoSolicitudSchema,
    SolicitudDocumentacionDetalleSchema,
    SolicitudDocumentacionSchema,
    TIPO_SOLICITUD_CONDUCTOR,
    TIPO_SOLICITUD_VEHICULO,
)
from app.services.notificacion import (
    crear_notificacion_resolucion_vehiculo,
    crear_notificacion_resolucion_conductor,
)


ESTADO_VEHICULO_EN_REVISION = "EN_REVISION"
ESTADO_CONDUCTOR_PENDIENTE = "PENDIENTE_REVISION"


def listar_solicitudes_pendientes(
    db: Session,
) -> list[SolicitudDocumentacionSchema]:
    """
    Lista todas las solicitudes de documentación pendientes de validación,
    unificando vehículos en EN_REVISION y documentación habilitante de
    conductores en PENDIENTE_REVISION.

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
                resumen=f"Licencia categoría {documentacion.categoria}",
            )
        )

    solicitudes.sort(key=lambda solicitud: solicitud.fecha_solicitud)

    return solicitudes


def obtener_detalle_solicitud_documentacion(
    db: Session,
    tipo: str,
    recurso_id,
) -> SolicitudDocumentacionDetalleSchema:
    """
    Abre el detalle documental de una solicitud existente (US 3R).

    Args:
        db: Sesion activa.
        tipo: VEHICULO o CONDUCTOR.
        recurso_id: UUID del vehiculo o de la documentacion habilitante.

    Raises:
        TipoSolicitudDocumentacionInvalidoError: Si el tipo no es soportado.
        SolicitudDocumentacionNoEncontradaError: Si el recurso no existe.
    """
    tipo_normalizado = tipo.strip().upper()

    if tipo_normalizado == TIPO_SOLICITUD_VEHICULO:
        return _obtener_detalle_vehiculo(db=db, recurso_id=recurso_id)

    if tipo_normalizado == TIPO_SOLICITUD_CONDUCTOR:
        return _obtener_detalle_conductor(db=db, recurso_id=recurso_id)

    raise TipoSolicitudDocumentacionInvalidoError()


def _documentos_desde_campos(campos: list[tuple[str, str | None]]) -> list[DocumentoSolicitudSchema]:
    """Convierte pares nombre/url en documentos visibles, omitiendo vacios."""
    return [
        DocumentoSolicitudSchema(nombre=nombre, url=url.strip())
        for nombre, url in campos
        if url and url.strip()
    ]


def _obtener_detalle_vehiculo(
    db: Session,
    recurso_id,
) -> SolicitudDocumentacionDetalleSchema:
    resultado = (
        db.query(Vehiculo, Usuario)
        .join(Usuario, Vehiculo.propietario_id == Usuario.id)
        .filter(Vehiculo.id == recurso_id)
        .first()
    )

    if resultado is None:
        raise SolicitudDocumentacionNoEncontradaError()

    vehiculo, propietario = resultado
    documentos = _documentos_desde_campos(
        [
            ("Cedula verde / titulo", vehiculo.cedula),
            ("Poliza de seguro", vehiculo.poliza),
            ("VTV / revision tecnica", vehiculo.vtv),
        ]
    )
    # Fotos del vehículo (lado como nombre) para la galería del admin.
    fotos = _documentos_desde_campos(
        [(foto.lado, foto.url) for foto in (vehiculo.fotos or [])]
    )

    return SolicitudDocumentacionDetalleSchema(
        tipo=TIPO_SOLICITUD_VEHICULO,
        recurso_id=vehiculo.id,
        usuario_id=propietario.id,
        usuario_email=propietario.email,
        estado=vehiculo.estado_registro,
        fecha_solicitud=vehiculo.updated_at,
        resumen=f"{vehiculo.marca} {vehiculo.modelo} ({vehiculo.anio})",
        documentos=documentos,
        fotos=fotos,
        kilometros=vehiculo.kilometros,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        anio=vehiculo.anio,
        tipo_transmision=vehiculo.tipo_transmision,
        capacidad=vehiculo.capacidad,
        categoria_vehiculo=vehiculo.categoria,
        tipo_combustible=vehiculo.tipo_combustible,
        pets_friendly=vehiculo.pets_friendly,
        patente=vehiculo.patente,
        chasis=vehiculo.chasis,
        motor=vehiculo.motor,
        titular=vehiculo.titular,
        estacion=vehiculo.estacion,
        telefono=vehiculo.telefono,
        descripcion=vehiculo.descripcion,
        motivo_rechazo=vehiculo.motivo_rechazo,
    )


def _obtener_detalle_conductor(
    db: Session,
    recurso_id,
) -> SolicitudDocumentacionDetalleSchema:
    resultado = (
        db.query(DocumentacionHabilitanteConductor, Usuario)
        .join(Usuario, DocumentacionHabilitanteConductor.usuario_id == Usuario.id)
        .filter(DocumentacionHabilitanteConductor.id == recurso_id)
        .first()
    )

    if resultado is None:
        raise SolicitudDocumentacionNoEncontradaError()

    documentacion, conductor = resultado
    documentos = _documentos_desde_campos(
        [
            ("Licencia frente", documentacion.foto_licencia_frente_url),
            ("Licencia dorso", documentacion.foto_licencia_dorso_url),
        ]
    )

    return SolicitudDocumentacionDetalleSchema(
        tipo=TIPO_SOLICITUD_CONDUCTOR,
        recurso_id=documentacion.id,
        usuario_id=conductor.id,
        usuario_email=conductor.email,
        estado=documentacion.estado_validacion,
        fecha_solicitud=documentacion.updated_at,
        resumen=f"Licencia categoría {documentacion.categoria}",
        documentos=documentos,
        categoria_licencia=documentacion.categoria,
        fecha_emision=documentacion.fecha_emision,
        fecha_vencimiento=documentacion.fecha_vencimiento,
        motivo_rechazo=documentacion.motivo_rechazo,
    )


def resolver_solicitud(
    db: Session,
    tipo: str,
    recurso_id,
    aprobada: bool,
    motivo_rechazo: str | None = None,
) -> None:
    """
    Resuelve una solicitud de documentación (aprueba o rechaza).
    
    Args:
        db: Sesion activa.
        tipo: VEHICULO o CONDUCTOR.
        recurso_id: UUID del recurso.
        aprobada: Booleano, True si se aprueba, False si se rechaza.
        motivo_rechazo: Texto con el motivo (obligatorio si aprobada es False).
        
    Raises:
        ValueError: Si se rechaza y el motivo_rechazo es vacío.
        TipoSolicitudDocumentacionInvalidoError: Si el tipo no es soportado.
        SolicitudDocumentacionNoEncontradaError: Si el recurso no existe.
    """
    tipo_normalizado = tipo.strip().upper()

    if not aprobada and (not motivo_rechazo or not motivo_rechazo.strip()):
        raise ValueError("El motivo de rechazo es obligatorio para rechazar la solicitud.")

    if tipo_normalizado == TIPO_SOLICITUD_VEHICULO:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == recurso_id).first()
        if not vehiculo:
            raise SolicitudDocumentacionNoEncontradaError()
            
        if aprobada:
            vehiculo.estado_registro = "HABILITADO"
            vehiculo.motivo_rechazo = None
        else:
            vehiculo.estado_registro = "RECHAZADO"
            vehiculo.motivo_rechazo = motivo_rechazo.strip()

        crear_notificacion_resolucion_vehiculo(
            db=db,
            vehiculo=vehiculo,
            aprobada=aprobada,
            motivo_rechazo=vehiculo.motivo_rechazo,
        )
            
        db.commit()
        return

    if tipo_normalizado == TIPO_SOLICITUD_CONDUCTOR:
        conductor = db.query(DocumentacionHabilitanteConductor).filter(
            DocumentacionHabilitanteConductor.id == recurso_id
        ).first()
        if not conductor:
            raise SolicitudDocumentacionNoEncontradaError()
            
        if aprobada:
            conductor.estado_validacion = EstadoHabilitacion.APROBADO
            conductor.motivo_rechazo = None
        else:
            conductor.estado_validacion = EstadoHabilitacion.RECHAZADO
            conductor.motivo_rechazo = motivo_rechazo.strip()
            
        crear_notificacion_resolucion_conductor(
            db=db,
            conductor=conductor,
            aprobada=aprobada,
            motivo_rechazo=conductor.motivo_rechazo,
        )

        db.commit()
        return

    raise TipoSolicitudDocumentacionInvalidoError()
