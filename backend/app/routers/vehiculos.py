"""
Controlador HTTP — Vehículos.

Endpoints:
    POST  /usuarios/{propietario_id}/vehiculos
    GET   /usuarios/{propietario_id}/vehiculos
    PATCH /vehiculos/{vehiculo_id}/precio
    PATCH /vehiculos/{vehiculo_id}/documentacion

Responsabilidades:
    1. Recibir y validar payloads HTTP.
    2. Exigir autenticación JWT en rutas sensibles.
    3. Verificar que el usuario autenticado opere solo sobre sus propios recursos.
    4. Delegar lógica de negocio a servicios.
    5. Traducir excepciones de dominio a respuestas HTTP.

Seguridad:
    - Para rutas con propietario_id:
        el claim `sub` del JWT debe coincidir con el propietario_id de la URL.
    - Para rutas con vehiculo_id:
        se verifica que el vehículo exista y que pertenezca al usuario autenticado.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    get_usuario_actual,
    requerir_rol_propietario,
    validar_usuario_autenticado_coincide_con_id,
)
from app.exceptions import (
    DocumentacionVehiculoNoEditableError,
    FotoVehiculoNoEncontradaError,
    MarcaModeloInexistenteError,
    UsuarioNoEncontradoError,
    VehiculoConReservaActivaError,
    VehiculoNoEncontradoError,
    VehiculoNoHabilitadoError,
)
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo import (
    CambiarDisponibilidadSchema,
    DefinirPrecioVehiculoSchema,
    DisponibilidadVehiculoResponseSchema,
    DocumentacionVehiculoSchema,
    FotoVehiculoPublicoSchema,
    FotoVehiculoSchema,
    PrecioVehiculoResponseSchema,
    ReemplazarFotoVehiculoSchema,
    RegistroVehiculoPayloadSchema,
    RegistroVehiculoSchema,
    VehiculoDocumentacionResponseSchema,
    VehiculoDetallePropietarioSchema,
    VehiculoPublicoSchema,
    ActualizarVehiculoPayloadSchema,
)
from app.services.vehiculo import (
    agregar_foto_a_vehiculo,
    cambiar_disponibilidad_vehiculo,
    cargar_documentacion_vehiculo,
    definir_precio_vehiculo,
    listar_vehiculos_por_propietario,
    reemplazar_foto_vehiculo,
    registrar_vehiculo,
    obtener_vehiculo,
    actualizar_vehiculo,
    listar_vehiculos_disponibles,
)
from app.models.documentacion_habilitante_conductor import (
    DocumentacionHabilitanteConductor,
    EstadoHabilitacion,
)


router = APIRouter(
    tags=["vehiculos"],
)


def validar_vehiculo_pertenece_a_usuario_autenticado(
    db: Session,
    vehiculo_id: uuid.UUID,
    usuario_actual: dict,
) -> None:
    """
    Verifica que un vehículo exista y pertenezca al usuario autenticado.

    Args:
        db: Sesión SQLAlchemy activa.
        vehiculo_id: UUID del vehículo recibido por path parameter.
        usuario_actual: Payload JWT validado.

    Raises:
        HTTPException 404:
            Si el vehículo no existe.
        HTTPException 403:
            Si el vehículo existe, pero pertenece a otro usuario.
    """
    vehiculo = (
        db.query(Vehiculo)
        .filter(Vehiculo.id == vehiculo_id)
        .first()
    )

    if vehiculo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(VehiculoNoEncontradoError()),
        )

    if str(vehiculo.propietario_id) != str(usuario_actual.get("sub")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede operar sobre un vehículo de otro usuario",
        )


@router.post(
    "/usuarios/{propietario_id}/vehiculos",
    response_model=VehiculoPublicoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar vehículo con características y fotos",
    description=(
        "Registra características obligatorias y fotos del vehículo. "
        "Requiere autenticación JWT y solo permite que el usuario autenticado "
        "registre vehículos para sí mismo."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Vehículo registrado exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta operar sobre otro propietario.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Propietario no encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Usuario no encontrado"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido.",
        },
    },
)
def registrar_vehiculo_usuario(
    propietario_id: uuid.UUID,
    payload: RegistroVehiculoPayloadSchema,
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> VehiculoPublicoSchema:
    """
    POST /usuarios/{propietario_id}/vehiculos

    Flujo:
        1. FastAPI valida propietario_id como UUID.
        2. FastAPI/Pydantic valida el payload.
        3. Se valida el JWT.
        4. Se verifica que propietario_id coincida con el `sub` del JWT.
        5. Se construye el schema de servicio incorporando propietario_id.
        6. El servicio verifica que el propietario exista y persiste el vehículo.
    """
    validar_usuario_autenticado_coincide_con_id(
        usuario_id=propietario_id,
        usuario_actual=usuario_actual,
    )

    schema = RegistroVehiculoSchema(
        propietario_id=propietario_id,
        **payload.model_dump(),
    )

    try:
        vehiculo = registrar_vehiculo(db=db, schema=schema)
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except MarcaModeloInexistenteError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return VehiculoPublicoSchema.model_validate(vehiculo)


@router.get(
    "/usuarios/{propietario_id}/vehiculos",
    response_model=list[VehiculoPublicoSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar vehículos publicados por un propietario",
    description=(
        "Lista los vehículos registrados por un usuario propietario. "
        "Requiere autenticación JWT y solo permite listar los vehículos "
        "del usuario autenticado."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Vehículos del propietario obtenidos exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta listar vehículos de otro usuario.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Propietario no encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Usuario no encontrado"}
                }
            },
        },
    },
)
def listar_vehiculos_usuario(
    propietario_id: uuid.UUID,
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> list[VehiculoPublicoSchema]:
    """
    GET /usuarios/{propietario_id}/vehiculos

    Flujo:
        1. FastAPI valida propietario_id como UUID.
        2. Se valida el JWT.
        3. Se verifica que propietario_id coincida con el `sub` del JWT.
        4. El servicio verifica que el propietario exista.
        5. Se devuelven los vehículos registrados por ese propietario.
    """
    validar_usuario_autenticado_coincide_con_id(
        usuario_id=propietario_id,
        usuario_actual=usuario_actual,
    )

    try:
        vehiculos = listar_vehiculos_por_propietario(
            db=db,
            propietario_id=propietario_id,
        )
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [
        VehiculoPublicoSchema.model_validate(vehiculo)
        for vehiculo in vehiculos
    ]


@router.get(
    "/vehiculos/catalogo",
    response_model=list[VehiculoPublicoSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar vehículos disponibles para alquilar",
    description=(
        "Obtiene el catálogo de vehículos habilitados y disponibles para alquiler. "
        "Requiere autenticación JWT."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Catálogo obtenido exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente o inválido.",
        },
    },
)
def listar_catalogo_vehiculos(
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> list[VehiculoPublicoSchema]:
    """
    GET /vehiculos/catalogo

    Flujo:
        1. Valida el JWT del usuario.
        2. Retorna la lista de vehículos habilitados y disponibles.
    """
    vehiculos = listar_vehiculos_disponibles(db=db)
    return [
        VehiculoPublicoSchema.model_validate(vehiculo)
        for vehiculo in vehiculos
    ]


@router.get(
    "/vehiculos/catalogo/{vehiculo_id}",
    response_model=VehiculoPublicoSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de un vehículo del catálogo",
    description=(
        "Obtiene el detalle de un vehículo específico del catálogo. "
        "Requiere autenticación JWT. Solo devuelve vehículos habilitados y disponibles."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Detalle del vehículo obtenido exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente o inválido.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Vehículo no encontrado o no disponible.",
        },
    },
)
def obtener_detalle_vehiculo_catalogo(
    vehiculo_id: uuid.UUID,
    usuario_actual: dict = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> VehiculoPublicoSchema:
    try:
        vehiculo = obtener_vehiculo(db=db, vehiculo_id=vehiculo_id)
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if vehiculo.estado_registro != "HABILITADO" or not vehiculo.disponible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El vehículo no está disponible para alquiler.",
        )

    return VehiculoPublicoSchema.model_validate(vehiculo)


@router.get(
    "/vehiculos/{vehiculo_id}",
    response_model=VehiculoDetallePropietarioSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de un vehículo",
    description=(
        "Obtiene el detalle de un vehículo, incluyendo su estado de registro "
        "y motivo de rechazo (si aplica). "
        "Requiere autenticación JWT y solo permite acceder a vehículos propios."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Detalle del vehículo obtenido exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta acceder a un vehículo ajeno.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Vehículo no encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Vehículo no encontrado"}
                }
            },
        },
    },
)
def obtener_detalle_vehiculo(
    vehiculo_id: uuid.UUID,
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> VehiculoDetallePropietarioSchema:
    """
    GET /vehiculos/{vehiculo_id}

    Flujo:
        1. FastAPI valida vehiculo_id como UUID.
        2. Se valida el JWT.
        3. Se verifica que el vehículo exista y pertenezca al usuario autenticado.
        4. Se devuelve el detalle del vehículo.
    """
    validar_vehiculo_pertenece_a_usuario_autenticado(
        db=db,
        vehiculo_id=vehiculo_id,
        usuario_actual=usuario_actual,
    )

    try:
        vehiculo = obtener_vehiculo(db=db, vehiculo_id=vehiculo_id)
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return VehiculoDetallePropietarioSchema.model_validate(vehiculo)


@router.patch(
    "/vehiculos/{vehiculo_id}/precio",
    response_model=PrecioVehiculoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Definir precio diario del vehículo",
    description=(
        "Define la tarifa diaria de alquiler para un vehículo existente. "
        "Requiere autenticación JWT y solo permite modificar vehículos "
        "propios. US 5D: solo precio por día, sin descuentos, comisión "
        "ni precio dinámico."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Precio diario definido exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta modificar un vehículo ajeno.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Vehículo no encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Vehiculo no encontrado"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido.",
        },
    },
)
def definir_precio_diario_vehiculo(
    vehiculo_id: uuid.UUID,
    payload: DefinirPrecioVehiculoSchema,
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> PrecioVehiculoResponseSchema:
    """
    PATCH /vehiculos/{vehiculo_id}/precio

    Flujo:
        1. FastAPI valida vehiculo_id como UUID.
        2. Pydantic valida que precio_por_dia sea mayor a cero.
        3. Se valida el JWT.
        4. Se verifica que el vehículo exista y pertenezca al usuario autenticado.
        5. El servicio persiste la tarifa diaria.
    """
    validar_vehiculo_pertenece_a_usuario_autenticado(
        db=db,
        vehiculo_id=vehiculo_id,
        usuario_actual=usuario_actual,
    )

    try:
        vehiculo = definir_precio_vehiculo(
            db=db,
            vehiculo_id=vehiculo_id,
            precio_por_dia=payload.precio_por_dia,
        )
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return PrecioVehiculoResponseSchema.model_validate(vehiculo)


@router.patch(
    "/vehiculos/{vehiculo_id}/documentacion",
    response_model=VehiculoDocumentacionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Cargar documentación legal del vehículo",
    description=(
        "Carga la documentación legal y operativa de un vehículo existente. "
        "Requiere autenticación JWT y solo permite modificar vehículos propios."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Documentación legal cargada exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta modificar un vehículo ajeno.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Vehículo no encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Vehiculo no encontrado"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido.",
        },
    },
)
def cargar_documentacion_legal_vehiculo(
    vehiculo_id: uuid.UUID,
    payload: DocumentacionVehiculoSchema,
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> VehiculoDocumentacionResponseSchema:
    """
    PATCH /vehiculos/{vehiculo_id}/documentacion

    Flujo:
        1. FastAPI valida vehiculo_id como UUID.
        2. Pydantic valida los campos documentales obligatorios.
        3. Se valida el JWT.
        4. Se verifica que el vehículo exista y pertenezca al usuario autenticado.
        5. El servicio persiste la documentación legal del vehículo.
    """
    validar_vehiculo_pertenece_a_usuario_autenticado(
        db=db,
        vehiculo_id=vehiculo_id,
        usuario_actual=usuario_actual,
    )

    try:
        vehiculo = cargar_documentacion_vehiculo(
            db=db,
            vehiculo_id=vehiculo_id,
            schema=payload,
        )
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentacionVehiculoNoEditableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return VehiculoDocumentacionResponseSchema.model_validate(vehiculo)


@router.patch(
    "/vehiculos/{vehiculo_id}/disponibilidad",
    response_model=DisponibilidadVehiculoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Cambiar disponibilidad del vehículo",
    description=(
        "Cambia el estado de disponibilidad de un vehículo para alquiler. "
        "Requiere autenticación JWT y solo permite modificar vehículos propios. "
        "El vehículo debe estar habilitado."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Disponibilidad cambiada exitosamente.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "El vehículo no está habilitado o tiene reservas activas.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta modificar un vehículo ajeno.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Vehículo no encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Vehiculo no encontrado"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido.",
        },
    },
)
def cambiar_disponibilidad_de_vehiculo(
    vehiculo_id: uuid.UUID,
    payload: CambiarDisponibilidadSchema,
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> DisponibilidadVehiculoResponseSchema:
    """
    PATCH /vehiculos/{vehiculo_id}/disponibilidad

    Flujo:
        1. FastAPI valida vehiculo_id como UUID y el payload.
        2. Se valida el JWT y que el vehículo pertenezca al usuario.
        3. El servicio verifica el estado_registro y si hay alquileres activos.
        4. Se actualiza el estado de disponibilidad.
    """
    validar_vehiculo_pertenece_a_usuario_autenticado(
        db=db,
        vehiculo_id=vehiculo_id,
        usuario_actual=usuario_actual,
    )

    try:
        vehiculo = cambiar_disponibilidad_vehiculo(
            db=db,
            vehiculo_id=vehiculo_id,
            disponible=payload.disponible,
        )
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (VehiculoNoHabilitadoError, VehiculoConReservaActivaError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return DisponibilidadVehiculoResponseSchema.model_validate(vehiculo)


@router.put(
    "/vehiculos/{vehiculo_id}",
    response_model=VehiculoPublicoSchema,
    status_code=status.HTTP_200_OK,
    summary="Actualizar datos y fotos de un vehículo",
    description=(
        "Actualiza las características de un vehículo y reemplaza sus fotos. "
        "No actualiza la marca ni el modelo por reglas de negocio. "
        "Requiere autenticación JWT y solo permite modificar vehículos propios."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Vehículo actualizado exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta modificar un vehículo ajeno.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Vehículo no encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Vehiculo no encontrado"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido.",
        },
    },
)
def actualizar_datos_vehiculo(
    vehiculo_id: uuid.UUID,
    payload: ActualizarVehiculoPayloadSchema,
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> VehiculoPublicoSchema:
    """
    PUT /vehiculos/{vehiculo_id}

    Flujo:
        1. FastAPI valida vehiculo_id y el payload.
        2. Se valida el JWT y que el vehículo pertenezca al usuario.
        3. El servicio actualiza las propiedades y reemplaza las fotos.
    """
    validar_vehiculo_pertenece_a_usuario_autenticado(
        db=db,
        vehiculo_id=vehiculo_id,
        usuario_actual=usuario_actual,
    )

    try:
        vehiculo = actualizar_vehiculo(
            db=db,
            vehiculo_id=vehiculo_id,
            schema=payload,
        )
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentacionVehiculoNoEditableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return VehiculoPublicoSchema.model_validate(vehiculo)


@router.post(
    "/vehiculos/{vehiculo_id}/fotos",
    response_model=FotoVehiculoPublicoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar una foto adicional a un vehículo existente",
    description=(
        "Agrega una foto al vehículo. Pensado para fotos del lado EXTRA "
        "subidas después del alta inicial, aunque admite cualquiera de los "
        "lados válidos. Requiere autenticación JWT y solo permite operar "
        "sobre vehículos del usuario autenticado."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Foto agregada exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta modificar un vehículo ajeno.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Vehículo no encontrado.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido.",
        },
    },
)
def agregar_foto_vehiculo_endpoint(
    vehiculo_id: uuid.UUID,
    payload: FotoVehiculoSchema,
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> FotoVehiculoPublicoSchema:
    """
    POST /vehiculos/{vehiculo_id}/fotos

    El cliente primero sube la imagen a Cloudinary vía /upload/foto-vehiculo
    (incluyendo lado=EXTRA si corresponde) y luego llama a este endpoint con
    la URL devuelta para persistirla asociada al vehículo.
    """
    validar_vehiculo_pertenece_a_usuario_autenticado(
        db=db,
        vehiculo_id=vehiculo_id,
        usuario_actual=usuario_actual,
    )

    try:
        foto = agregar_foto_a_vehiculo(
            db=db,
            vehiculo_id=vehiculo_id,
            lado=payload.lado,
            url=payload.url,
            formato=payload.formato,
            tamanio_bytes=payload.tamanio_bytes,
        )
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return FotoVehiculoPublicoSchema.model_validate(foto)


@router.put(
    "/vehiculos/{vehiculo_id}/fotos/{foto_id}",
    response_model=FotoVehiculoPublicoSchema,
    status_code=status.HTTP_200_OK,
    summary="Reemplazar una foto existente de un vehículo",
    description=(
        "Reemplaza la imagen de una foto ya asociada a un vehículo, "
        "conservando el lado original. El cliente sube primero la nueva "
        "imagen a Cloudinary y luego invoca este endpoint con la URL "
        "devuelta. Requiere autenticación JWT y solo permite operar sobre "
        "vehículos del usuario autenticado."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Foto reemplazada exitosamente.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o invalidado.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El usuario autenticado intenta modificar un vehículo ajeno.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Vehículo o foto no encontrados.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Payload inválido.",
        },
    },
)
def reemplazar_foto_de_vehiculo(
    vehiculo_id: uuid.UUID,
    foto_id: uuid.UUID,
    payload: ReemplazarFotoVehiculoSchema,
    usuario_actual: dict = Depends(requerir_rol_propietario),
    db: Session = Depends(get_db),
) -> FotoVehiculoPublicoSchema:
    """
    PUT /vehiculos/{vehiculo_id}/fotos/{foto_id}

    Flujo:
        1. Se valida el JWT y que el vehículo pertenezca al usuario autenticado.
        2. El servicio actualiza url, formato y tamaño manteniendo el `lado`.
    """
    validar_vehiculo_pertenece_a_usuario_autenticado(
        db=db,
        vehiculo_id=vehiculo_id,
        usuario_actual=usuario_actual,
    )

    try:
        foto = reemplazar_foto_vehiculo(
            db=db,
            vehiculo_id=vehiculo_id,
            foto_id=foto_id,
            url=payload.url,
            formato=payload.formato,
            tamanio_bytes=payload.tamanio_bytes,
        )
    except VehiculoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except FotoVehiculoNoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return FotoVehiculoPublicoSchema.model_validate(foto)
    return FotoVehiculoPublicoSchema.model_validate(foto)
