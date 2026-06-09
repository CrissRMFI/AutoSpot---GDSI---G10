"""
Servicio de negocio — Web Push.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.push_subscription import PushSubscription
from app.schemas.push_subscription import PushSubscriptionCreateSchema

try:
    from pywebpush import WebPushException, webpush
except ImportError:  # pragma: no cover - pywebpush se instala en producción.
    WebPushException = None
    webpush = None


logger = logging.getLogger(__name__)

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:admin@autospot.local")


def push_configurado() -> bool:
    return bool(webpush and VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY)


def registrar_suscripcion_push(
    db: Session,
    usuario_id: uuid.UUID,
    schema: PushSubscriptionCreateSchema,
    user_agent: str | None = None,
) -> PushSubscription:
    """
    Crea o actualiza la suscripción Push del navegador/dispositivo.
    """
    endpoint = schema.endpoint.strip()
    existente = (
        db.query(PushSubscription)
        .filter(PushSubscription.endpoint == endpoint)
        .first()
    )

    if existente is None:
        suscripcion = PushSubscription(
            usuario_id=usuario_id,
            endpoint=endpoint,
            p256dh=schema.keys.p256dh,
            auth=schema.keys.auth,
            user_agent=user_agent,
        )
        db.add(suscripcion)
    else:
        suscripcion = existente
        suscripcion.usuario_id = usuario_id
        suscripcion.p256dh = schema.keys.p256dh
        suscripcion.auth = schema.keys.auth
        suscripcion.user_agent = user_agent
        suscripcion.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(suscripcion)
    return suscripcion


def eliminar_suscripcion_push(
    db: Session,
    usuario_id: uuid.UUID,
    endpoint: str,
    commit: bool = True,
) -> bool:
    """
    Elimina una suscripción puntual del usuario.
    """
    endpoint_limpio = (endpoint or "").strip()
    if not endpoint_limpio:
        return False

    suscripcion = (
        db.query(PushSubscription)
        .filter(
            PushSubscription.usuario_id == usuario_id,
            PushSubscription.endpoint == endpoint_limpio,
        )
        .first()
    )
    if suscripcion is None:
        return False

    db.delete(suscripcion)
    if commit:
        db.commit()
    return True


def enviar_push_a_usuario(
    db: Session,
    usuario_id: uuid.UUID,
    titulo: str,
    mensaje: str,
    data: dict[str, Any] | None = None,
) -> int:
    """
    Envía una notificación Web Push a todas las suscripciones del usuario.

    Si VAPID o pywebpush no están configurados, no interfiere con el flujo
    principal de negocio: la notificación in-app sigue persistiendo.
    """
    if not push_configurado():
        return 0

    suscripciones = (
        db.query(PushSubscription)
        .filter(PushSubscription.usuario_id == usuario_id)
        .all()
    )
    if not suscripciones:
        return 0

    payload = json.dumps({
        "title": titulo,
        "body": mensaje,
        "data": data or {},
    })
    enviados = 0

    for suscripcion in suscripciones:
        subscription_info = {
            "endpoint": suscripcion.endpoint,
            "keys": {
                "p256dh": suscripcion.p256dh,
                "auth": suscripcion.auth,
            },
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_SUBJECT},
            )
            enviados += 1
        except Exception as exc:  # noqa: BLE001 - no debe romper el flujo principal.
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if WebPushException is not None and isinstance(exc, WebPushException):
                logger.warning(
                    "Fallo Web Push para usuario %s endpoint %s: %s",
                    usuario_id,
                    suscripcion.endpoint,
                    exc,
                )
            else:
                logger.exception("Error enviando Web Push")

            if status_code in {404, 410}:
                db.delete(suscripcion)

    return enviados
