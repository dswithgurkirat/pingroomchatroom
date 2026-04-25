"""
Sticker catalogue routes.
"""

from fastapi import APIRouter, Depends

from app.core.supabase import get_supabase_client
from app.middleware.auth import CurrentUser
from app.models.schemas import StickerCreate, StickerResponse
from app.services.sticker_service import StickerService

router = APIRouter()


def _sticker_service() -> StickerService:
    return StickerService(get_supabase_client())


@router.get("/", response_model=list[StickerResponse])
async def list_stickers(
    _: CurrentUser,
    service: StickerService = Depends(_sticker_service),
):
    """Browse the sticker catalogue."""
    return await service.list_stickers()


@router.get("/my-stickers", response_model=list[StickerResponse])
async def my_stickers(
    current_user: CurrentUser,
    service: StickerService = Depends(_sticker_service),
):
    """Return all stickers purchased by the current user."""
    return await service.get_user_purchases(current_user.user_id)


@router.post("/", response_model=StickerResponse, status_code=201)
async def create_sticker(
    data: StickerCreate,
    current_user: CurrentUser,
    service: StickerService = Depends(_sticker_service),
):
    """
    Add a sticker to the catalogue.
    In production, restrict this to admin users via RLS or a role check.
    """
    return await service.create_sticker(data)
