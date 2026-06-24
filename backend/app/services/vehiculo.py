"""
Servicio de negocio — US 1D: Cargar características y fotos del auto.

Responsabilidades de esta capa:
    1. Verificar que el propietario exista como Usuario base.
    2. Registrar características obligatorias del vehículo.
    3. Registrar fotos asociadas.
    4. Persistir el vehículo con estado inicial PENDIENTE_DOCUMENTACION.

Esta capa NO valida campos obligatorios, año, formato o cantidad de fotos;
esas responsabilidades pertenecen al schema Pydantic.
"""
import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.exceptions import (
    ActualizarDocumentacionVehiculoConReservaActivaError,
    ActualizarDocumentacionVehiculoDisponibleError,
    DocumentacionVehiculoNoEditableError,
    DocumentacionVehiculoNoExistenteError,
    FotoVehiculoNoEncontradaError,
    MarcaModeloInexistenteError,
    UsuarioNoEncontradoError,
    VehiculoConReporteActivoError,
    VehiculoNoEncontradoError,
    VehiculoNoHabilitadoError,
    VehiculoConReservaActivaError,
)
from app.models.foto_vehiculo import FotoVehiculo
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.models.valoracion import Valoracion
from app.models.testimonio import Testimonio
from app.models.usuario import Usuario
from app.models.datos_personales_usuario import DatosPersonalesUsuario
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo import (
    DocumentacionVehiculoSchema,
    RegistroVehiculoSchema,
    ActualizarVehiculoPayloadSchema,
)
from app.services.marca_service import validar_combo_marca_modelo
from app.services.reporte_service import obtener_reporte_activo_por_vehiculo
from app.services.notificacion import (
    cerrar_notificacion_documentacion_pendiente,
    crear_notificacion_documentacion_pendiente,
)


ESTADOS_DOCUMENTACION_EDITABLE = {"PENDIENTE_DOCUMENTACION", "RECHAZADO"}
ESTADO_DOCUMENTACION_CORREGIBLE = "RECHAZADO"
ESTADO_DOCUMENTACION_ACTUALIZABLE = "HABILITADO"
CAMBIOS_DOCUMENTALES_ACTUALIZACION = (
    "patente",
    "chasis",
    "motor",
    "titular",
    "estacion",
    "telefono",
)
ESTADOS_RESERVA_QUE_BLOQUEAN_DISPONIBILIDAD = {
    "CONFIRMADA",
    "CODIGO_GENERADO",
    "VERIFICADA",
    "EN_CURSO",
    "ENTREGA_SOLICITADA",
    "DEVUELTO",
    "CHECKOUT_PENDIENTE",
}

def registrar_vehiculo(db: Session, schema: RegistroVehiculoSchema) -> Vehiculo:
    """
    Registra un vehículo con sus características y fotos.

    Flujo:
        1. Verifica que exista el Usuario propietario.
        2. Crea el Vehiculo con estado inicial PENDIENTE_DOCUMENTACION.
        3. Crea las FotoVehiculo asociadas.
        4. Persiste y retorna el Vehiculo hidratado.

    Args:
        db     : Sesión SQLAlchemy activa.
        schema : Payload ya validado por RegistroVehiculoSchema.

    Returns:
        Vehiculo persistido con sus fotos asociadas.

    Raises:
        UsuarioNoEncontradoError: Si el propietario no existe.
        MarcaModeloInexistenteError: Si la combinación marca/modelo no está
            registrada en el catálogo (tablas `marcas`/`modelos`).
    """
    propietario = (
        db.query(Usuario)
        .filter(Usuario.id == schema.propietario_id)
        .first()
    )
    if propietario is None:
        raise UsuarioNoEncontradoError()

    validar_combo_marca_modelo(db, marca=schema.marca, modelo=schema.modelo)

    vehiculo = Vehiculo(
      propietario_id=schema.propietario_id,
      marca=schema.marca,
      modelo=schema.modelo,
      anio=schema.anio,
      tipo_transmision=schema.tipo_transmision,
      capacidad=schema.capacidad,
      categoria=schema.categoria,
      tipo_combustible=schema.tipo_combustible,
      pets_friendly=schema.pets_friendly,
      kilometros=schema.kilometros,
    )

    vehiculo.fotos = [
        FotoVehiculo(
            lado=foto.lado,
            url=foto.url,
            formato=foto.formato,
            tamanio_bytes=foto.tamanio_bytes,
        )
        for foto in schema.fotos
    ]

    db.add(vehiculo)
    db.flush()
    crear_notificacion_documentacion_pendiente(db=db, vehiculo=vehiculo)
    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def actualizar_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    schema: ActualizarVehiculoPayloadSchema
) -> Vehiculo:
    """
    Actualiza las características y fotos de un vehículo.
    No actualiza marca ni modelo para mantener integridad con reservas/reglas de negocio.
    Reemplaza todas las fotos por las nuevas provistas.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    cambios_documentales = any(
        getattr(schema, campo) is not None
        and getattr(schema, campo) != getattr(vehiculo, campo)
        for campo in CAMBIOS_DOCUMENTALES_ACTUALIZACION
    )
    if (
        cambios_documentales
        and vehiculo.estado_registro != ESTADO_DOCUMENTACION_CORREGIBLE
    ):
        raise DocumentacionVehiculoNoEditableError()

    # Se actualizan las características generales, ignorando marca y modelo
    vehiculo.anio = schema.anio
    vehiculo.tipo_transmision = schema.tipo_transmision
    vehiculo.capacidad = schema.capacidad
    vehiculo.categoria = schema.categoria
    vehiculo.tipo_combustible = schema.tipo_combustible
    vehiculo.pets_friendly = schema.pets_friendly

    # Actualizar campos de documentación opcionales
    if schema.patente is not None: vehiculo.patente = schema.patente
    if schema.chasis is not None: vehiculo.chasis = schema.chasis
    if schema.motor is not None: vehiculo.motor = schema.motor
    if schema.titular is not None: vehiculo.titular = schema.titular
    if schema.estacion is not None: vehiculo.estacion = schema.estacion
    if schema.telefono is not None: vehiculo.telefono = schema.telefono

    # Reemplazar fotos (debido a cascade delete-orphan, las viejas se borran)
    vehiculo.fotos = [
        FotoVehiculo(
            lado=foto.lado,
            url=foto.url,
            formato=foto.formato,
            tamanio_bytes=foto.tamanio_bytes,
        )
        for foto in schema.fotos
    ]

    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def definir_precio_vehiculo(
    db: Session,
    vehiculo_id,
    precio_por_dia,
) -> Vehiculo:
    """
    Define la tarifa diaria de un vehículo existente.

    US 5D — Alcance actual:
        - guarda precio por día
        - sin descuentos
        - sin comisión
        - sin precio dinámico
        - sin moneda múltiple

    Args:
        db             : Sesión SQLAlchemy activa.
        vehiculo_id    : Identificador del vehículo.
        precio_por_dia : Tarifa diaria validada por capas superiores.

    Returns:
        Vehiculo actualizado.

    Nota:
        La validación de vehículo inexistente se completará en el siguiente
        bloque de TDD con una excepción de dominio específica.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    vehiculo.precio_por_dia = precio_por_dia

    db.commit()
    db.refresh(vehiculo)

    return vehiculo

def obtener_vehiculo(db: Session, vehiculo_id: uuid.UUID) -> Vehiculo:
    """
    Obtiene un vehículo por su ID.

    Args:
        db: Sesión SQLAlchemy.
        vehiculo_id: UUID del vehículo.

    Returns:
        Vehiculo: El vehículo si existe.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    return vehiculo

def agregar_foto_a_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    lado: str,
    url: str,
    formato: str,
    tamanio_bytes: int,
) -> FotoVehiculo:
    """
    Agrega una foto adicional a un vehículo existente.

    Pensado para fotos del lado EXTRA cargadas después del alta inicial,
    aunque admite cualquier lado válido.

    Args:
        db            : Sesión SQLAlchemy activa.
        vehiculo_id   : UUID del vehículo.
        lado          : Lado de la foto (FRENTE/TRASERA/...EXTRA).
        url           : URL pública devuelta por Cloudinary.
        formato       : Formato del archivo (jpg/jpeg/png/webp).
        tamanio_bytes : Tamaño del archivo subido en bytes.

    Returns:
        La FotoVehiculo persistida.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )
    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    foto = FotoVehiculo(
        vehiculo_id=vehiculo_id,
        lado=lado,
        url=url,
        formato=formato,
        tamanio_bytes=tamanio_bytes,
    )

    db.add(foto)
    db.commit()
    db.refresh(foto)

    return foto


def reemplazar_foto_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    foto_id: uuid.UUID,
    url: str,
    formato: str,
    tamanio_bytes: int,
) -> FotoVehiculo:
    """
    Reemplaza la URL y metadata de una foto existente de un vehículo.

    El cliente sube primero la imagen nueva a Cloudinary (manteniendo el
    `lado` original) y luego invoca este servicio para persistir la nueva
    URL en la foto ya asociada al vehículo.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
        FotoVehiculoNoEncontradaError: Si la foto no existe o no pertenece
            al vehículo indicado.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )
    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    foto = (
        db.query(FotoVehiculo)
        .filter(
            FotoVehiculo.id == foto_id,
            FotoVehiculo.vehiculo_id == vehiculo_id,
        )
        .first()
    )
    if foto is None:
        raise FotoVehiculoNoEncontradaError()

    foto.url = url
    foto.formato = formato
    foto.tamanio_bytes = tamanio_bytes

    db.commit()
    db.refresh(foto)

    return foto


def listar_vehiculos_por_propietario(db: Session, propietario_id) -> list[Vehiculo]:
    """
    Lista los vehículos registrados por un propietario.

    Alcance Sprint 1:
        - permite verificar desde el dashboard que los vehículos publicados
          quedaron registrados.
        - no implementa catálogo público.
        - no implementa filtros, reservas, edición ni eliminación.
    """
    propietario = (
        db.query(Usuario)
        .filter(Usuario.id == propietario_id)
        .first()
    )

    if propietario is None:
        raise UsuarioNoEncontradoError()

    vehiculos = (
        db.query(Vehiculo)
        .filter(Vehiculo.propietario_id == propietario_id)
        .all()
    )

    # Marca cuáles tienen un alquiler/reserva activo para poder distinguir en el
    # frontend "Alquilado" (tiene alquiler) de "No disponible" (pausado por el dueño).
    ids = [vehiculo.id for vehiculo in vehiculos]
    ids_alquilados = set()
    if ids:
        filas = (
            db.query(Reserva.vehiculo_id)
            .filter(
                Reserva.vehiculo_id.in_(ids),
                Reserva.estado.in_(ESTADOS_RESERVA_QUE_BLOQUEAN_DISPONIBILIDAD),
            )
            .all()
        )
        ids_alquilados = {fila[0] for fila in filas}

    for vehiculo in vehiculos:
        vehiculo.alquilado = vehiculo.id in ids_alquilados

    return vehiculos

def cargar_documentacion_vehiculo(
    db: Session,
    vehiculo_id,
    schema: DocumentacionVehiculoSchema,
) -> Vehiculo:
    """
    Carga la documentación legal y operativa de un vehículo existente.

    Carga la documentación legal y operativa de un vehículo existente.

    Este flujo actualiza el estado de la solicitud para que un administrador
    lo revise (US 4D).

    Args:
        db          : Sesión SQLAlchemy activa.
        vehiculo_id : Identificador del vehículo.
        schema      : Payload documental validado por Pydantic.

    Returns:
        Vehiculo actualizado con documentación legal.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    if vehiculo.estado_registro not in ESTADOS_DOCUMENTACION_EDITABLE:
        raise DocumentacionVehiculoNoEditableError()

    vehiculo.patente = schema.patente
    vehiculo.chasis = schema.chasis
    vehiculo.motor = schema.motor
    vehiculo.titular = schema.titular
    vehiculo.cedula = schema.cedula
    vehiculo.poliza = schema.poliza
    vehiculo.vtv = schema.vtv
    vehiculo.estacion = schema.estacion
    vehiculo.telefono = schema.telefono
    vehiculo.descripcion = schema.descripcion
    
    # Cambia a estado EN_REVISION para la US 4D
    vehiculo.estado_registro = "EN_REVISION"
    # Si estaba rechazado, limpiamos el motivo
    vehiculo.motivo_rechazo = None
    cerrar_notificacion_documentacion_pendiente(db=db, vehiculo=vehiculo)

    db.commit()
    db.refresh(vehiculo)

    return vehiculo

def actualizar_documentacion_vehiculo(
        db: Session,
        vehiculo_id: uuid.UUID,
        schema: DocumentacionVehiculoSchema,

) -> Vehiculo:
    """
    Actualiza la documentación legal y operativa de un vehículo existente.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    if vehiculo.estado_registro != ESTADO_DOCUMENTACION_ACTUALIZABLE:
        raise DocumentacionVehiculoNoExistenteError()
    
    if vehiculo.disponible == True:
        raise ActualizarDocumentacionVehiculoDisponibleError()
    
    if verificar_alquileres_activos(db=db, vehiculo_id=vehiculo_id):
        raise ActualizarDocumentacionVehiculoConReservaActivaError()
    

    vehiculo.patente = schema.patente
    vehiculo.chasis = schema.chasis
    vehiculo.motor = schema.motor
    vehiculo.titular = schema.titular
    vehiculo.cedula = schema.cedula
    vehiculo.poliza = schema.poliza
    vehiculo.vtv = schema.vtv
    vehiculo.estacion = schema.estacion
    vehiculo.telefono = schema.telefono
    vehiculo.descripcion = schema.descripcion
    
    # Cambia a estado EN_REVISION para la US 4D
    vehiculo.estado_registro = "EN_REVISION"
    # Si estaba rechazado, limpiamos el motivo
    vehiculo.motivo_rechazo = None

    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def verificar_alquileres_activos(db: Session, vehiculo_id: uuid.UUID) -> bool:
    """
    Verifica si un vehículo tiene reservas o alquileres que bloquean su baja
    de disponibilidad.
    """
    reserva_activa = (
        db.query(Reserva.id)
        .filter(
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.estado.in_(ESTADOS_RESERVA_QUE_BLOQUEAN_DISPONIBILIDAD),
        )
        .first()
    )
    return reserva_activa is not None


def cambiar_disponibilidad_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    disponible: bool,
) -> Vehiculo:
    """
    Cambia el estado de disponibilidad del vehículo para alquiler.

    Args:
        db: Sesión SQLAlchemy.
        vehiculo_id: UUID del vehículo.
        disponible: Nuevo estado de disponibilidad (True/False).

    Returns:
        Vehiculo actualizado.

    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
        VehiculoNoHabilitadoError: Si el auto no está HABILITADO.
        VehiculoConReservaActivaError: Si se intenta deshabilitar y tiene alquileres.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    if vehiculo.estado_registro != "HABILITADO":
        raise VehiculoNoHabilitadoError()

    # Un auto con un alquiler/reserva activo no puede cambiar su disponibilidad
    # en ninguna dirección: no se puede volver a marcar como disponible mientras
    # está alquilado, ni "deshabilitarlo" porque ya está comprometido.
    if verificar_alquileres_activos(db=db, vehiculo_id=vehiculo_id):
        raise VehiculoConReservaActivaError()

    # No se puede reactivar la disponibilidad mientras exista un reporte critico activo.
    if disponible and obtener_reporte_activo_por_vehiculo(db=db, vehiculo_id=vehiculo_id):
        raise VehiculoConReporteActivoError()

    vehiculo.disponible = disponible

    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def listar_vehiculos_disponibles(
    db: Session,
    puntuacion_minima: Decimal | float | None = None,
    usuario_actual: dict | None = None,
) -> list[Vehiculo]:
    """
    Lista todos los vehículos que están habilitados y disponibles para alquiler,
    y que tienen un precio por día definido.

    US 8C — Motor de filtrado de catálogo por puntuación:
        Si se recibe `puntuacion_minima`, se devuelven únicamente los vehículos
        cuya calificación promedio sea mayor o igual a ese valor (CA 1). Los
        vehículos sin calificación (aún sin valoraciones) quedan excluidos
        cuando se aplica el filtro, ya que no alcanzan la puntuación pedida.
        Si `puntuacion_minima` es None, se devuelve el catálogo completo (CA 4).

    Args:
        db: Sesión SQLAlchemy activa.
        puntuacion_minima: Puntuación mínima (1 a 5) a exigir, o None.

    Returns:
        Lista de vehículos disponibles que cumplen el filtro.
    """
    query = db.query(Vehiculo).filter(
        Vehiculo.estado_registro == "HABILITADO",
        Vehiculo.disponible == True,
        Vehiculo.precio_por_dia.isnot(None),
        Vehiculo.precio_por_dia > 0,
        ~db.query(Reserva.id)
        .filter(
            Reserva.vehiculo_id == Vehiculo.id,
            Reserva.estado.in_(ESTADOS_RESERVA_QUE_BLOQUEAN_DISPONIBILIDAD),
        )
        .exists(),
    )

    if puntuacion_minima is not None:
        query = query.filter(
            Vehiculo.calificacion_promedio.isnot(None),
            Vehiculo.calificacion_promedio >= puntuacion_minima,
        )

    if usuario_actual and usuario_actual.get("sub"):
        from app.models.usuario import Usuario
        usuario = db.query(Usuario).filter(Usuario.id == usuario_actual.get("sub")).first()
        if usuario and (usuario.rol or "").upper() == "PROPIETARIO":
            query = query.filter(Vehiculo.propietario_id == usuario.id)

    return query.all()


def cambiar_ubicacion_vehiculo(
    db: Session,
    vehiculo_id: uuid.UUID,
    estacion: str | None,
) -> Vehiculo:
    """
    Cambia la ubicación (estación) actual del vehículo manualmente.

    Args:
        db: Sesión SQLAlchemy activa.
        vehiculo_id: Identificador del vehículo.
        estacion: Nombre de la estación, o None si está en alquiler/fuera.

    Returns:
        Vehiculo actualizado.
    
    Raises:
        VehiculoNoEncontradoError: Si el vehículo no existe.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise VehiculoNoEncontradoError()

    vehiculo.estacion = estacion

    db.commit()
    db.refresh(vehiculo)

    return vehiculo

def obtener_resenias_vehiculo(db: Session, vehiculo_id: uuid.UUID) -> list[dict]:
    """
    Obtiene el listado de reseñas (Valoración + Testimonio) para un vehículo (US 10C).
    Realiza un JOIN entre Valoracion, Testimonio y Usuario.
    """
    from sqlalchemy import desc

    # Verificamos si existe el vehículo
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise VehiculoNoEncontradoError()

    # Query que junta Valoracion con datos del conductor y hace left join con Testimonio.
    resultados = (
        db.query(Valoracion, Testimonio, DatosPersonalesUsuario)
        .join(DatosPersonalesUsuario, Valoracion.conductor_id == DatosPersonalesUsuario.usuario_id)
        .outerjoin(Testimonio, Testimonio.reserva_id == Valoracion.reserva_id)
        .filter(Valoracion.vehiculo_id == vehiculo_id)
        .order_by(desc(Valoracion.created_at))
        .all()
    )

    resenias = []
    for val, test, usr in resultados:
        if usr:
            conductor_str = f"{usr.nombre} {usr.apellido}"
        else:
            conductor_str = "Conductor Anónimo"

        resenias.append({
            "id_reserva": val.reserva_id,
            "puntaje": float(val.puntaje),
            "descripcion": test.descripcion if test else None,
            "conductor": conductor_str,
            "fecha": val.created_at,
        })

    return resenias

def obtener_historial_uso_vehiculo(db: Session, vehiculo_id: uuid.UUID) -> list[dict]:
    """
    Obtiene el historial de uso de un vehículo.
    """
    from sqlalchemy import desc
    from app.models.checkout_vehiculo import CheckoutVehiculo
    from app.models.checkin_vehiculo import CheckinVehiculo
    from app.models.reporte import Reporte

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise VehiculoNoEncontradoError()

    resultados = (
        db.query(Reserva, DatosPersonalesUsuario, Testimonio, Valoracion, CheckoutVehiculo, CheckinVehiculo, Reporte)
        .join(DatosPersonalesUsuario, Reserva.conductor_id == DatosPersonalesUsuario.usuario_id)
        .outerjoin(Testimonio, Testimonio.reserva_id == Reserva.id)
        .outerjoin(Valoracion, Valoracion.reserva_id == Reserva.id)
        .outerjoin(CheckoutVehiculo, CheckoutVehiculo.reserva_id == Reserva.id)
        .outerjoin(CheckinVehiculo, CheckinVehiculo.reserva_id == Reserva.id)
        .outerjoin(Reporte, Reporte.reserva_id == Reserva.id)
        .filter(Reserva.vehiculo_id == vehiculo_id)
        .order_by(desc(Reserva.created_at))
        .all()
    )

    historial = []
    for res, usr, test, val, checkout, checkin, reporte in resultados:
        fotos = []
        if checkout:
            fotos.extend([
                checkout.url_foto_frente, checkout.url_foto_trasera, 
                checkout.url_foto_lateral_izq, checkout.url_foto_lateral_der, 
                checkout.url_foto_panel
            ])
            if checkout.url_foto_extra:
                fotos.append(checkout.url_foto_extra)
            if checkout.urls_fotos_danios:
                fotos.extend(checkout.urls_fotos_danios)
        elif checkin:
            fotos.extend([
                checkin.url_foto_frente, checkin.url_foto_trasera, 
                checkin.url_foto_lateral_izq, checkin.url_foto_lateral_der, 
                checkin.url_foto_panel
            ])
            if checkin.url_foto_extra:
                fotos.append(checkin.url_foto_extra)
            if checkin.urls_fotos_danios:
                fotos.extend(checkin.urls_fotos_danios)

        tiene_reporte = False
        detalles_reporte = None
        
        # Check para reportes o rechazos
        ci_danios = checkin.descripcion_danios if checkin else None
        ci_rechazo = checkin.motivo_rechazo if checkin else None
        co_danios = checkout.descripcion_danios if checkout else None
        co_rechazo = checkout.motivo_rechazo if checkout else None
        
        reporte_incidencia = None
        fecha_devolucion_real_res = res.fecha_devolucion_real

        if reporte:
            reporte_incidencia = {
                "descripcion": reporte.descripcion,
                "resolucion_descripcion": reporte.resolucion_descripcion,
                "fotos": [foto.url for foto in reporte.fotos] if reporte.fotos else [],
                "created_at": reporte.created_at,
                "resuelto_at": reporte.resuelto_at
            }
            if not fecha_devolucion_real_res:
                fecha_devolucion_real_res = reporte.created_at
        
        if (checkin and (checkin.tiene_danios or checkin.estado == "RECHAZADO")) or \
           (checkout and (checkout.tiene_danios or checkout.estado == "RECHAZADO")) or \
           reporte:
            tiene_reporte = True
            detalles_reporte = {
                "descripcion_danios_checkin": ci_danios,
                "motivo_rechazo_checkin": ci_rechazo,
                "descripcion_danios_checkout": co_danios,
                "motivo_rechazo_checkout": co_rechazo,
                "reporte_incidencia": reporte_incidencia,
            }

        historial.append({
            "conductor_nombre": f"{usr.nombre} {usr.apellido}",
            "fecha_inicio": res.fecha_inicio,
            "fecha_fin": res.fecha_fin,
            "fecha_devolucion_real": fecha_devolucion_real_res,
            "puntaje": val.puntaje if val else None,
            "resenia": test.descripcion if test else None,
            "fotos_entrega": fotos,
            "tiene_reporte": tiene_reporte,
            "detalles_reporte": detalles_reporte,
        })

    return historial
