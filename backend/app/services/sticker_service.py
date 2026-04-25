"""
Sticker catalogue service.
"""

import logging
from uuid import UUID

from fastapi import HTTPException
from supabase import Client

from app.models.schemas import StickerCreate, StickerResponse

logger = logging.getLogger(__name__)


class StickerService:
    def __init__(self, client: Client):
        self.client = client

    async def list_stickers(self) -> list[StickerResponse]:
        try:
            result = self.client.table("stickers").select("*").order("name").execute()
            return [StickerResponse(**row) for row in result.data]
        except Exception as exc:
            logger.error(f"list_stickers error: {exc}")
            raise HTTPException(status_code=500, detail="Could not fetch stickers")

    async def get_sticker(self, sticker_id: UUID) -> StickerResponse:
        try:
            result = (
                self.client.table("stickers")
                .select("*")
                .eq("id", str(sticker_id))
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Sticker not found")
            return StickerResponse(**result.data)
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"get_sticker error: {exc}")
            raise HTTPException(status_code=404, detail="Sticker not found")

    async def create_sticker(self, data: StickerCreate) -> StickerResponse:
        """Admin-only operation (enforce at route level)."""
        try:
            result = (
                self.client.table("stickers")
                .insert({"name": data.name, "price": data.price, "url": data.url})
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create sticker")
            logger.info(f"Sticker created: {result.data[0]['id']}")
            return StickerResponse(**result.data[0])
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"create_sticker error: {exc}")
            raise HTTPException(status_code=500, detail="Could not create sticker")

    async def get_user_purchases(self, user_id: str) -> list[StickerResponse]:
        """Return all stickers a user has purchased."""
        try:
            result = (
                self.client.table("purchases")
                .select("sticker_id, stickers(*)")
                .eq("user_id", user_id)
                .execute()
            )
            stickers = [
                StickerResponse(**row["stickers"])
                for row in result.data
                if row.get("stickers")
            ]
            return stickers
        except Exception as exc:
            logger.error(f"get_user_purchases error: {exc}")
            raise HTTPException(status_code=500, detail="Could not fetch purchases")
