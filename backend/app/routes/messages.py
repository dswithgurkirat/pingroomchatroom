"""
Message routes — send and retrieve messages per room.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentUser
from app.models.schemas import MessageCreate, MessageResponse, MessageListResponse, SuccessResponse
from app.services.message_service import MessageService

router = APIRouter()


def _message_service() -> MessageService:
    # Use service-role client since our API already authenticates users
    # and the local Supabase RLS policies can block inserts in dev setups.
    return MessageService(get_supabase_admin())


@router.post("/", response_model=MessageResponse, status_code=201)
async def send_message(
    data: MessageCreate,
    current_user: CurrentUser,
    service: MessageService = Depends(_message_service),
):
    """Send a message to a chat room. Requires authentication."""
    return await service.send_message(data, current_user.user_id)


@router.get("/room/{room_id}", response_model=MessageListResponse)
async def get_messages(
    room_id: UUID,
    _: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    service: MessageService = Depends(_message_service),
):
    """
    Fetch messages for a room with pagination.

    - **page**: page number (1-indexed)
    - **page_size**: messages per page (max 200)
    """
    return await service.get_messages_by_room(room_id, page=page, page_size=page_size)


@router.delete("/{message_id}", response_model=SuccessResponse)
async def delete_message(
    message_id: UUID,
    current_user: CurrentUser,
    service: MessageService = Depends(_message_service),
):
    """Delete your own message."""
    await service.delete_message(message_id, current_user.user_id)
    return SuccessResponse(message="Message deleted")
