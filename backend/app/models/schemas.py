"""
Pydantic schemas (request / response models) for PingRoom.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, HttpUrl, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


# ── Rooms ─────────────────────────────────────────────────────────────────────

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class RoomResponse(BaseModel):
    id: UUID
    name: str
    created_by: str
    created_at: datetime


# ── Messages ──────────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    room_id: UUID
    message: str = Field(..., min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    id: UUID
    user_id: str
    room_id: UUID
    message: str
    created_at: datetime


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
    page: int
    page_size: int


# ── Stickers ──────────────────────────────────────────────────────────────────

class StickerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    url: str


class StickerResponse(BaseModel):
    id: UUID
    name: str
    price: float
    url: str


# ── Payments ──────────────────────────────────────────────────────────────────

class CheckoutSessionRequest(BaseModel):
    sticker_id: UUID


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class PurchaseResponse(BaseModel):
    id: UUID
    user_id: str
    sticker_id: UUID
    payment_id: str
    created_at: datetime


# ── Generic ───────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str


class SuccessResponse(BaseModel):
    message: str
    success: bool = True
