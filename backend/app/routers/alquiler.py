"""
Endpoints HTTP para la gestión de alquileres.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_admin, requerir_rol_cliente
from app.exceptions import (
    MotivoRechazoRequeridoError,
    ReservaActivaExistenteError,
    ReservaCodigoYaVerificadoError,
    ReservaNoEncontradaError,
    ReservaNoRechazableError,
    VehiculoNoDisponibleParaReservaError,
    VehiculoNoEncontradoError,
)
from app.schemas.alquiler import (
    ConductorReservaResumenSchema,
    CrearReservaPayloadSchema,
    RechazarReservaPayloadSchema,
    ReservaCodigoResponseSchema,
    ReservaVerificacionResponseSchema,
    SimularTiempoAlquilerRequest,
    SimularTiempoAlquilerResponse,
    VerificarCodigoReservaPayloadSchema,
    VehiculoReservaResumenSchema,
)
from app.services.alquiler_service import (
    buscar_reserva_por_codigo,
    calcular_tiempo_alquiler,
    crear_reserva_con_codigo,
    listar_reservas_de_conductor,
    motivo_bloqueo_entrega,
    obtener_datos_personales_de_conductor,
    obtener_reserva_admin,
    rechazar_reserva,
    verificar_codigo_reserva,
)

router = APIRouter(
    prefix="/alquiler",
    tags=["Alquiler"]
)


def _vehiculo_resumen(reserva) -> VehiculoReservaResumenSchema:
    vehiculo = reserva.vehiculo
    return VehiculoReservaResumenSchema(
        id=vehiculo.id,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        patente=vehiculo.patente,
        estacion=reserva.estacion_retiro,
    )


def _reserva_codigo_response(reserva) -> ReservaCodigoResponseSchema:
    return ReservaCodigoResponseSchema(
        id=reserva.id,
        vehiculo_id=reserva.vehiculo_id,
        conductor_id=reserva.conductor_id,
        estado=reserva.estado,
        codigo_reserva=reserva.codigo,
        codigo_verificado_at=reserva.codigo_verificado_at,
        fecha_inicio=reserva.fecha_inicio,
        fecha_fin=reserva.fecha_fin,
        monto_total=reserva.monto_total,
        estacion_retiro=reserva.estacion_retiro,
        motivo_rechazo=reserva.motivo_rechazo,
        vehiculo=_vehiculo_resumen(reserva),
    )


def _reserva_verificacion_response(
    db: Session,
    reserva,
) -> ReservaVerificacionResponseSchema:
    datos_personales = obtener_datos_personales_de_conductor(
        db=db,
        conductor_id=reserva.conductor_id,
    )
    motivo_bloqueo = motivo_bloqueo_entrega(reserva)

    return ReservaVerificacionResponseSchema(
        **_reserva_codigo_response(reserva).model_dump(),
        conductor=ConductorReservaResumenSchema(
            id=reserva.conductor.id,
            email=reserva.conductor.email,
            nombre=datos_personales.nombre if datos_personales else None,
            apellido=datos_personales.apellido if datos_personales else None,
            dni=datos_personales.dni if datos_personales else None,
        ),
        puede_entregar=reserva.codigo_verificado_at is not None and motivo_bloqueo is None,
        motivo_bloqueo=motivo_bloqueo,
    )


@router.post(
    "/simular-tiempo",
    response_model=SimularTiempoAlquilerResponse,
    status_code=status.HTTP_200_OK,
    summary="Simular y validar tiempo de alquiler",
)
def simular_tiempo(payload: SimularTiempoAlquilerRequest):
    """
    Verifica que el periodo definido entre la fecha de inicio y fin sea válido
    (mínimo 1 día) y calcula la duración total exacta en días y horas.
    """
    try:
        resultado = calcular_tiempo_alquiler(payload.fecha_inicio, payload.fecha_fin)
        return SimularTiempoAlquilerResponse(**resultado)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post(
    "/reservas",
    response_model=ReservaCodigoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Confirmar reserva y obtener código",
)
def crear_reserva(
    payload: CrearReservaPayloadSchema,
    usuario_actual: dict = Depends(requerir_rol_cliente),
    db: Session = Depends(get_db),
) -> ReservaCodigoResponseSchema:
    """
    US 14C — Crea una reserva confirmada y devuelve el código de retiro.
    """
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))

    try:
        reserva = crear_reserva_con_codigo(
            db=db,
            schema=payload,
            conductor_id=conductor_id,
        )
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (VehiculoNoDisponibleParaReservaError, ReservaActivaExistenteError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return _reserva_codigo_response(reserva)


@router.get(
    "/reservas",
    response_model=list[ReservaCodigoResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar reservas del cliente autenticado",
)
def listar_mis_reservas(
    usuario_actual: dict = Depends(requerir_rol_cliente),
    db: Session = Depends(get_db),
) -> list[ReservaCodigoResponseSchema]:
    """
    Devuelve las reservas del conductor autenticado para la pantalla Mis reservas.
    """
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))
    reservas = listar_reservas_de_conductor(db=db, conductor_id=conductor_id)

    return [
        _reserva_codigo_response(reserva)
        for reserva in reservas
    ]


@router.get(
    "/reservas/admin/{reserva_id}",
    response_model=ReservaVerificacionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de reserva para verificación",
)
def obtener_reserva_para_verificacion(
    reserva_id: uuid.UUID,
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> ReservaVerificacionResponseSchema:
    """
    US 5R — Devuelve el detalle completo que el recepcionista necesita para
    verificar identidad y reserva.
    """
    try:
        reserva = obtener_reserva_admin(db=db, reserva_id=reserva_id)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return _reserva_verificacion_response(db=db, reserva=reserva)


@router.post(
    "/reservas/admin/buscar-por-codigo",
    response_model=ReservaVerificacionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar reserva por código sin marcarla como usada",
)
def consultar_reserva_por_codigo(
    payload: VerificarCodigoReservaPayloadSchema,
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> ReservaVerificacionResponseSchema:
    """
    Lookup admin que devuelve el detalle de una reserva por código.
    No marca el código como verificado.
    """
    try:
        reserva = buscar_reserva_por_codigo(
            db=db,
            codigo_reserva=payload.codigo_reserva,
        )
    except ReservaNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return _reserva_verificacion_response(db=db, reserva=reserva)


@router.post(
    "/reservas/admin/{reserva_id}/rechazar",
    response_model=ReservaVerificacionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Rechazar reserva",
)
def rechazar_reserva_endpoint(
    reserva_id: uuid.UUID,
    payload: RechazarReservaPayloadSchema,
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> ReservaVerificacionResponseSchema:
    """
    Rechaza una reserva pendiente con un motivo, libera el vehículo al
    catálogo y notifica al conductor.
    """
    try:
        reserva = rechazar_reserva(
            db=db,
            reserva_id=reserva_id,
            motivo=payload.motivo,
        )
    except ReservaNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except MotivoRechazoRequeridoError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ReservaNoRechazableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return _reserva_verificacion_response(db=db, reserva=reserva)


@router.post(
    "/reservas/verificar-codigo",
    response_model=ReservaVerificacionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Verificar código de reserva",
)
def verificar_codigo_de_reserva(
    payload: VerificarCodigoReservaPayloadSchema,
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> ReservaVerificacionResponseSchema:
    """
    Verifica un código de reserva una sola vez. Luego de la primera
    verificación, el mismo código queda inválido para futuros usos.
    """
    try:
        reserva = verificar_codigo_reserva(
            db=db,
            codigo_reserva=payload.codigo_reserva,
        )
    except ReservaNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ReservaCodigoYaVerificadoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return _reserva_verificacion_response(db=db, reserva=reserva)
