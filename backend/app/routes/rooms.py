"""
Chat room routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentUser
from app.models.schemas import RoomCreate, RoomResponse, SuccessResponse
from app.services.room_service import RoomService

router = APIRouter()


def _room_service() -> RoomService:
    # Use service-role client since our API already authenticates users
    # and the local Supabase RLS policies can block inserts in dev setups.
    return RoomService(get_supabase_admin())


@router.get("/", response_model=list[RoomResponse])
async def list_rooms(
    _: CurrentUser,
    service: RoomService = Depends(_room_service),
):
    """List all available chat rooms."""
    return await service.list_rooms()


@router.post("/", response_model=RoomResponse, status_code=201)
async def create_room(
    data: RoomCreate,
    current_user: CurrentUser,
    service: RoomService = Depends(_room_service),
):
    """Create a new chat room."""
    return await service.create_room(data, current_user.user_id)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: UUID,
    _: CurrentUser,
    service: RoomService = Depends(_room_service),
):
    """Get details for a specific room."""
    return await service.get_room(room_id)


@router.delete("/{room_id}", response_model=SuccessResponse)
async def delete_room(
    room_id: UUID,
    current_user: CurrentUser,
    service: RoomService = Depends(_room_service),
):
    """Delete a room (creator only)."""
    await service.delete_room(room_id, current_user.user_id)
    return SuccessResponse(message="Room deleted successfully")
