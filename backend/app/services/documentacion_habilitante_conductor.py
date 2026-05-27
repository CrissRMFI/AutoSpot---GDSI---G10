"""
Servicio de negocio — US 1C: Documentación habilitante del Conductor.

Responsabilidades de esta capa:
    1. Verificar que el Usuario exista.
    2. Registrar/actualizar la licencia de conducir y sus fotos.
    3. Persistir el registro asociado al Usuario.
    4. Dejar estado inicial de validación en PENDIENTE_VALIDACION.

Esta capa NO valida campos obligatorios vacíos ni fechas inconsistentes;
esa responsabilidad pertenece al schema Pydantic.
"""
import uuid

from sqlalchemy.orm import Session

from app.exceptions import (
    DocumentacionHabilitanteNoRegistradaError,
    DocumentacionHabilitanteYaRegistradaError,
    UsuarioNoEncontradoError,
)
from app.models.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductor,
    EstadoHabilitacion,
)
from app.models.usuario import Usuario
from app.schemas.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductorSchema,
)


def registrar_documentacion_habilitante(
    db: Session,
    usuario_id: uuid.UUID,
    schema: DocumentacionHabilitanteConductorSchema,
) -> DocumentacionHabilitanteConductor:
    """
    Registra la documentación habilitante (licencia de conducir) de un Conductor.

    Flujo:
        1. Verifica que exista el Usuario.
        2. Verifica que no exista una documentación previa para ese Usuario.
        3. Persiste el registro y lo retorna hidratado.

    Raises:
        UsuarioNoEncontradoError: Si el Usuario no existe.
        DocumentacionHabilitanteYaRegistradaError: Si ya tiene documentación.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise UsuarioNoEncontradoError()

    documentacion_existente = (
        db.query(DocumentacionHabilitanteConductor)
        .filter(DocumentacionHabilitanteConductor.usuario_id == usuario_id)
        .first()
    )
    if documentacion_existente is not None:
        raise DocumentacionHabilitanteYaRegistradaError()

    documentacion = DocumentacionHabilitanteConductor(
        usuario_id=usuario_id,
        numero_licencia=schema.numero_licencia,
        categoria=schema.categoria,
        fecha_emision=schema.fecha_emision,
        fecha_vencimiento=schema.fecha_vencimiento,
        foto_licencia_frente_url=schema.foto_licencia_frente_url,
        foto_licencia_dorso_url=schema.foto_licencia_dorso_url,
    )

    db.add(documentacion)
    db.commit()
    db.refresh(documentacion)

    return documentacion


def obtener_documentacion_habilitante(
    db: Session,
    usuario_id: uuid.UUID,
) -> DocumentacionHabilitanteConductor:
    """
    Retorna la documentación habilitante de un Conductor existente.

    Raises:
        UsuarioNoEncontradoError: Si el Usuario no existe.
        DocumentacionHabilitanteNoRegistradaError: Si aún no fue cargada.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise UsuarioNoEncontradoError()

    documentacion = (
        db.query(DocumentacionHabilitanteConductor)
        .filter(DocumentacionHabilitanteConductor.usuario_id == usuario_id)
        .first()
    )
    if documentacion is None:
        raise DocumentacionHabilitanteNoRegistradaError()

    return documentacion


def actualizar_documentacion_habilitante(
    db: Session,
    usuario_id: uuid.UUID,
    schema: DocumentacionHabilitanteConductorSchema,
) -> DocumentacionHabilitanteConductor:
    """
    Actualiza la documentación habilitante de un Conductor existente.

    Flujo:
        1. Verifica que exista el Usuario.
        2. Verifica que existan datos previos para actualizar.
        3. Actualiza el registro y lo retorna hidratado.

    Raises:
        UsuarioNoEncontradoError: Si el Usuario no existe.
        DocumentacionHabilitanteNoRegistradaError: Si no hay datos previos.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise UsuarioNoEncontradoError()

    documentacion = (
        db.query(DocumentacionHabilitanteConductor)
        .filter(DocumentacionHabilitanteConductor.usuario_id == usuario_id)
        .first()
    )
    if documentacion is None:
        raise DocumentacionHabilitanteNoRegistradaError()

    documentacion.numero_licencia = schema.numero_licencia
    documentacion.categoria = schema.categoria
    documentacion.fecha_emision = schema.fecha_emision
    documentacion.fecha_vencimiento = schema.fecha_vencimiento
    documentacion.foto_licencia_frente_url = schema.foto_licencia_frente_url
    documentacion.foto_licencia_dorso_url = schema.foto_licencia_dorso_url

    db.commit()
    db.refresh(documentacion)

    return documentacion


def aprobar_documentacion_habilitante(
    db: Session,
    usuario_id: uuid.UUID,
) -> DocumentacionHabilitanteConductor:
    """
    Aprueba la documentación habilitante de un Conductor.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise UsuarioNoEncontradoError()

    documentacion = (
        db.query(DocumentacionHabilitanteConductor)
        .filter(DocumentacionHabilitanteConductor.usuario_id == usuario_id)
        .first()
    )
    if documentacion is None:
        raise DocumentacionHabilitanteNoRegistradaError()

    documentacion.estado_validacion = EstadoHabilitacion.APROBADO
    documentacion.motivo_rechazo = None

    db.commit()
    db.refresh(documentacion)

    return documentacion
