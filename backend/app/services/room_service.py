"""
Room management service.
"""

import logging
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.models.schemas import RoomCreate, RoomResponse

logger = logging.getLogger(__name__)


class RoomService:
    def __init__(self, client: Client):
        self.client = client

    async def create_room(self, data: RoomCreate, user_id: str) -> RoomResponse:
        try:
            result = (
                self.client.table("rooms")
                .insert({"name": data.name, "created_by": user_id})
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create room")

            row = result.data[0]
            logger.info(f"Room created: {row['id']} by user {user_id}")
            return RoomResponse(**row)
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"create_room error: {exc}")
            raise HTTPException(status_code=500, detail="Could not create room")

    async def list_rooms(self) -> list[RoomResponse]:
        try:
            result = (
                self.client.table("rooms")
                .select("*")
                .order("created_at", desc=False)
                .execute()
            )
            return [RoomResponse(**row) for row in result.data]
        except Exception as exc:
            logger.error(f"list_rooms error: {exc}")
            raise HTTPException(status_code=500, detail="Could not fetch rooms")

    async def get_room(self, room_id: UUID) -> RoomResponse:
        try:
            result = (
                self.client.table("rooms")
                .select("*")
                .eq("id", str(room_id))
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Room not found")
            return RoomResponse(**result.data)
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"get_room error: {exc}")
            raise HTTPException(status_code=404, detail="Room not found")

    async def delete_room(self, room_id: UUID, user_id: str) -> None:
        """Only the creator can delete their room."""
        room = await self.get_room(room_id)
        if room.created_by != user_id:
            raise HTTPException(status_code=403, detail="Not authorised to delete this room")
        try:
            self.client.table("rooms").delete().eq("id", str(room_id)).execute()
            logger.info(f"Room deleted: {room_id}")
        except Exception as exc:
            logger.error(f"delete_room error: {exc}")
            raise HTTPException(status_code=500, detail="Could not delete room")
