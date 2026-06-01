"""
Endpoints HTTP para la gestión de alquileres.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import requerir_rol_admin, requerir_rol_cliente
from app.exceptions import (
    CheckoutNoConfirmableError,
    CheckoutNoDisponibleError,
    CheckoutNoEncontradoError,
    MotivoRechazoRequeridoError,
    ReservaActivaExistenteError,
    ReservaCodigoYaVerificadoError,
    ReservaNoEnCursoError,
    ReservaNoEncontradaError,
    ReservaNoEntregableError,
    ReservaNoRechazableError,
    ReservaSinCheckinAprobadoError,
    VehiculoNoDisponibleParaReservaError,
    VehiculoNoEncontradoError,
)
from app.schemas.alquiler import (
    ConductorReservaResumenSchema,
    CrearReservaPayloadSchema,
    PaginaReservasSchema,
    RechazarReservaPayloadSchema,
    ReservaCodigoResponseSchema,
    ReservaVerificacionResponseSchema,
    SimularTiempoAlquilerRequest,
    SimularTiempoAlquilerResponse,
    VerificarCodigoReservaPayloadSchema,
    VehiculoReservaResumenSchema,
)
from app.schemas.checkout_vehiculo import (
    CheckoutResponseSchema,
    RechazarCheckoutPayloadSchema,
)
from app.services.alquiler_service import (
    buscar_reserva_por_codigo,
    calcular_tiempo_alquiler,
    crear_reserva_con_codigo,
    entregar_auto,
    listar_mis_alquileres,
    listar_recepcion,
    listar_reservas_de_conductor,
    listar_reservas_para_entregar,
    motivo_bloqueo_entrega,
    obtener_alquiler_conductor,
    obtener_datos_personales_de_conductor,
    obtener_reserva_admin,
    registrar_entrada,
    rechazar_reserva,
    registrar_salida,
    verificar_codigo_reserva,
)
from app.services.checkout_service import (
    confirmar_checkout,
    obtener_checkout_vigente,
    rechazar_checkout,
)
from app.models.estacion import Estacion
from app.schemas.estacion import EstacionDetailResponse

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
        anio=vehiculo.anio,
        tipo_transmision=vehiculo.tipo_transmision,
        capacidad=vehiculo.capacidad,
        categoria=vehiculo.categoria,
        tipo_combustible=vehiculo.tipo_combustible,
        pets_friendly=vehiculo.pets_friendly,
        patente=vehiculo.patente,
        descripcion=vehiculo.descripcion,
        precio_por_dia=vehiculo.precio_por_dia,
        estacion=reserva.estacion_retiro,
        fotos=[
            {
                "id": foto.id,
                "lado": foto.lado,
                "url": foto.url,
            }
            for foto in getattr(vehiculo, "fotos", [])
        ],
    )


def _reserva_codigo_response(db: Session, reserva) -> ReservaCodigoResponseSchema:
    estacion_detalle = None
    if reserva.estado not in ["PENDIENTE", "RECHAZADA"]:
        estacion_db = db.query(Estacion).filter(Estacion.nombre == reserva.estacion_retiro).first()
        if estacion_db:
            estacion_detalle = EstacionDetailResponse.model_validate(estacion_db)

    return ReservaCodigoResponseSchema(
        id=reserva.id,
        vehiculo_id=reserva.vehiculo_id,
        conductor_id=reserva.conductor_id,
        estado=reserva.estado,
        codigo_reserva=reserva.codigo,
        codigo_verificado_at=reserva.codigo_verificado_at,
        fecha_inicio=reserva.fecha_inicio,
        fecha_fin=reserva.fecha_fin,
        fecha_entrega_solicitada=reserva.fecha_entrega_solicitada,
        fecha_salida_real=reserva.fecha_salida_real,
        fecha_devolucion_real=reserva.fecha_devolucion_real,
        monto_total=reserva.monto_total,
        estacion_retiro=reserva.estacion_retiro,
        motivo_rechazo=reserva.motivo_rechazo,
        minutos_retraso=reserva.minutos_retraso,
        monto_penalizacion=reserva.monto_penalizacion,
        vehiculo=_vehiculo_resumen(reserva),
        estacion_detalle=estacion_detalle,
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
        **_reserva_codigo_response(db, reserva).model_dump(),
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


def _pagina(db: Session, items, total, page, size) -> PaginaReservasSchema:
    pages = (total + size - 1) // size if size else 1
    return PaginaReservasSchema(
        items=[_reserva_codigo_response(db, r) for r in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
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
    """US 14C — Crea una reserva confirmada y devuelve el código de retiro."""
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))

    try:
        reserva = crear_reserva_con_codigo(
            db=db,
            schema=payload,
            conductor_id=conductor_id,
        )
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (VehiculoNoDisponibleParaReservaError, ReservaActivaExistenteError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return _reserva_codigo_response(db, reserva)


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
    """Reservas del conductor autenticado (pantalla Mis reservas)."""
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))
    reservas = listar_reservas_de_conductor(db=db, conductor_id=conductor_id)
    return [_reserva_codigo_response(db, reserva) for reserva in reservas]


# ── Conductor: Mis alquileres (US 22C) ────────────────────────────────────────
@router.get(
    "/mis-alquileres",
    response_model=PaginaReservasSchema,
    status_code=status.HTTP_200_OK,
    summary="Listar mis alquileres (paginado)",
)
def listar_mis_alquileres_endpoint(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    usuario_actual: dict = Depends(requerir_rol_cliente),
    db: Session = Depends(get_db),
) -> PaginaReservasSchema:
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))
    items, total = listar_mis_alquileres(db=db, conductor_id=conductor_id, page=page, size=size)
    return _pagina(db, items, total, page, size)


# ── Admin: listados (literales antes de /reservas/admin/{reserva_id}) ─────────
@router.get(
    "/reservas/admin/para-entregar",
    response_model=list[ReservaCodigoResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar reservas listas para entregar (US 6R)",
)
def listar_para_entregar_endpoint(
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> list[ReservaCodigoResponseSchema]:
    """Reservas VERIFICADA con check-in aprobado, listas para la salida."""
    return [
        _reserva_codigo_response(db, reserva)
        for reserva in listar_reservas_para_entregar(db=db)
    ]


@router.get(
    "/reservas/admin/recepcion",
    response_model=PaginaReservasSchema,
    status_code=status.HTTP_200_OK,
    summary="Listar autos para recibir/checkout (paginado, US 7R/8R)",
)
def listar_recepcion_endpoint(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> PaginaReservasSchema:
    items, total = listar_recepcion(db=db, page=page, size=size)
    return _pagina(db, items, total, page, size)


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
    """Lookup admin de una reserva por código (no marca verificación)."""
    try:
        reserva = buscar_reserva_por_codigo(db=db, codigo_reserva=payload.codigo_reserva)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
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
    """Verifica un código de reserva una sola vez."""
    try:
        reserva = verificar_codigo_reserva(db=db, codigo_reserva=payload.codigo_reserva)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ReservaCodigoYaVerificadoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _reserva_verificacion_response(db=db, reserva=reserva)


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
    """US 5R — Detalle completo para verificar identidad y reserva."""
    try:
        reserva = obtener_reserva_admin(db=db, reserva_id=reserva_id)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
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
    """Rechaza una reserva pendiente, libera el vehículo y notifica al conductor."""
    try:
        reserva = rechazar_reserva(db=db, reserva_id=reserva_id, motivo=payload.motivo)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except MotivoRechazoRequeridoError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except ReservaNoRechazableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _reserva_verificacion_response(db=db, reserva=reserva)


@router.post(
    "/reservas/admin/{reserva_id}/registrar-salida",
    response_model=ReservaCodigoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Registrar salida del auto (US 6R)",
)
def registrar_salida_endpoint(
    reserva_id: uuid.UUID,
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> ReservaCodigoResponseSchema:
    """US 6R — Marca el alquiler como iniciado (EN_CURSO). Requiere check-in aprobado."""
    try:
        reserva = registrar_salida(db=db, reserva_id=reserva_id)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ReservaNoEntregableError, ReservaSinCheckinAprobadoError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _reserva_codigo_response(db, reserva)


@router.post(
    "/reservas/admin/{reserva_id}/registrar-entrada",
    response_model=ReservaCodigoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Registrar entrada del auto (US 7R)",
)
def registrar_entrada_endpoint(
    reserva_id: uuid.UUID,
    _usuario_actual: dict = Depends(requerir_rol_admin),
    db: Session = Depends(get_db),
) -> ReservaCodigoResponseSchema:
    """US 7R — Registra recepción, congela fecha real y calcula penalización."""
    try:
        reserva = registrar_entrada(db=db, reserva_id=reserva_id)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ReservaNoEnCursoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _reserva_codigo_response(db, reserva)


# ── Conductor: entrega del auto y confirmación de checkout (US 22C) ───────────
@router.post(
    "/reservas/{reserva_id}/entregar",
    response_model=ReservaCodigoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Conductor entrega/devuelve el auto (US 22C)",
)
def entregar_auto_endpoint(
    reserva_id: uuid.UUID,
    usuario_actual: dict = Depends(requerir_rol_cliente),
    db: Session = Depends(get_db),
) -> ReservaCodigoResponseSchema:
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))
    try:
        reserva = entregar_auto(db=db, reserva_id=reserva_id, conductor_id=conductor_id)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ReservaNoEnCursoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _reserva_codigo_response(db, reserva)


@router.get(
    "/reservas/{reserva_id}/checkout",
    response_model=CheckoutResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener el checkout vigente del alquiler (conductor)",
)
def obtener_checkout_de_reserva_endpoint(
    reserva_id: uuid.UUID,
    usuario_actual: dict = Depends(requerir_rol_cliente),
    db: Session = Depends(get_db),
) -> CheckoutResponseSchema:
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))
    try:
        obtener_alquiler_conductor(db=db, reserva_id=reserva_id, conductor_id=conductor_id)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    checkout = obtener_checkout_vigente(db=db, reserva_id=reserva_id)
    if checkout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay checkout para esta reserva")
    return checkout


@router.get(
    "/reservas/{reserva_id}",
    response_model=ReservaCodigoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Detalle de mi alquiler (conductor)",
)
def obtener_mi_alquiler_endpoint(
    reserva_id: uuid.UUID,
    usuario_actual: dict = Depends(requerir_rol_cliente),
    db: Session = Depends(get_db),
) -> ReservaCodigoResponseSchema:
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))
    try:
        reserva = obtener_alquiler_conductor(db=db, reserva_id=reserva_id, conductor_id=conductor_id)
    except ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _reserva_codigo_response(db, reserva)


@router.post(
    "/checkouts/{checkout_id}/confirmar",
    response_model=CheckoutResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Conductor confirma el checkout (cierra el alquiler)",
)
def confirmar_checkout_endpoint(
    checkout_id: uuid.UUID,
    usuario_actual: dict = Depends(requerir_rol_cliente),
    db: Session = Depends(get_db),
) -> CheckoutResponseSchema:
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))
    try:
        return confirmar_checkout(db=db, checkout_id=checkout_id, conductor_id=conductor_id)
    except CheckoutNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CheckoutNoConfirmableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/checkouts/{checkout_id}/rechazar",
    response_model=CheckoutResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Conductor rechaza el checkout (con motivo)",
)
def rechazar_checkout_endpoint(
    checkout_id: uuid.UUID,
    payload: RechazarCheckoutPayloadSchema,
    usuario_actual: dict = Depends(requerir_rol_cliente),
    db: Session = Depends(get_db),
) -> CheckoutResponseSchema:
    conductor_id = uuid.UUID(str(usuario_actual["sub"]))
    try:
        return rechazar_checkout(
            db=db,
            checkout_id=checkout_id,
            conductor_id=conductor_id,
            motivo=payload.motivo,
        )
    except CheckoutNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except MotivoRechazoRequeridoError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except CheckoutNoConfirmableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
