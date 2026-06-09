"""
Schemas Pydantic — Suscripciones Web Push.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PushSubscriptionKeysSchema(BaseModel):
    p256dh: str = Field(..., min_length=1)
    auth: str = Field(..., min_length=1)


class PushSubscriptionCreateSchema(BaseModel):
    endpoint: str = Field(..., min_length=1, max_length=1024)
    expirationTime: int | None = None
    keys: PushSubscriptionKeysSchema


class PushSubscriptionDeleteSchema(BaseModel):
    endpoint: str = Field(..., min_length=1, max_length=1024)


class PushSubscriptionSchema(BaseModel):
    id: uuid.UUID
    usuario_id: uuid.UUID
    endpoint: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
