"""
Message service — send and retrieve chat messages.
"""

import logging
from uuid import UUID

from fastapi import HTTPException
from supabase import Client

from app.models.schemas import MessageCreate, MessageResponse, MessageListResponse

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


class MessageService:
    def __init__(self, client: Client):
        self.client = client

    async def send_message(self, data: MessageCreate, user_id: str) -> MessageResponse:
        try:
            result = (
                self.client.table("messages")
                .insert(
                    {
                        "user_id": user_id,
                        "room_id": str(data.room_id),
                        "message": data.message,
                    }
                )
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to send message")

            row = result.data[0]
            logger.info(f"Message sent by {user_id} in room {data.room_id}")
            return MessageResponse(**row)
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"send_message error: {exc}")
            raise HTTPException(status_code=500, detail="Could not send message")

    async def get_messages_by_room(
        self,
        room_id: UUID,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> MessageListResponse:
        page_size = min(page_size, MAX_PAGE_SIZE)
        offset = (page - 1) * page_size

        try:
            # Count total messages in room
            count_result = (
                self.client.table("messages")
                .select("id", count="exact")
                .eq("room_id", str(room_id))
                .execute()
            )
            total = count_result.count or 0

            # Fetch paginated messages
            result = (
                self.client.table("messages")
                .select("*")
                .eq("room_id", str(room_id))
                .order("created_at", desc=False)
                .range(offset, offset + page_size - 1)
                .execute()
            )

            messages = [MessageResponse(**row) for row in result.data]
            return MessageListResponse(
                messages=messages,
                total=total,
                page=page,
                page_size=page_size,
            )
        except Exception as exc:
            logger.error(f"get_messages_by_room error: {exc}")
            raise HTTPException(status_code=500, detail="Could not fetch messages")

    async def delete_message(self, message_id: UUID, user_id: str) -> None:
        """Users can only delete their own messages."""
        try:
            result = (
                self.client.table("messages")
                .select("user_id")
                .eq("id", str(message_id))
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Message not found")
            if result.data["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Not authorised")

            self.client.table("messages").delete().eq("id", str(message_id)).execute()
            logger.info(f"Message {message_id} deleted by {user_id}")
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"delete_message error: {exc}")
            raise HTTPException(status_code=500, detail="Could not delete message")
