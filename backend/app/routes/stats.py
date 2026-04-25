"""
Analytics / stats routes — aggregated data for the dashboard charts.
"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from app.core.supabase import get_supabase_client
from app.middleware.auth import CurrentUser
from supabase import Client

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_client() -> Client:
    return get_supabase_client()


@router.get("/overview")
async def get_overview(
    _: CurrentUser,
    client: Client = Depends(_get_client),
):
    """
    Return high-level stats: total rooms, total messages, and active-today count.
    """
    try:
        rooms_result = client.table("rooms").select("id", count="exact").execute()
        total_rooms = rooms_result.count or 0

        msgs_result = client.table("messages").select("id", count="exact").execute()
        total_messages = msgs_result.count or 0

        # Messages sent today
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        today_result = (
            client.table("messages")
            .select("id", count="exact")
            .gte("created_at", today_start)
            .execute()
        )
        messages_today = today_result.count or 0

        return {
            "total_rooms": total_rooms,
            "total_messages": total_messages,
            "messages_today": messages_today,
        }
    except Exception as exc:
        logger.error(f"stats overview error: {exc}")
        return {"total_rooms": 0, "total_messages": 0, "messages_today": 0}


@router.get("/messages-per-day")
async def messages_per_day(
    _: CurrentUser,
    client: Client = Depends(_get_client),
):
    """
    Return message counts for the last 7 days (for an area/line chart).
    """
    try:
        days = []
        now = datetime.now(timezone.utc)
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)

            result = (
                client.table("messages")
                .select("id", count="exact")
                .gte("created_at", day_start.isoformat())
                .lte("created_at", day_end.isoformat())
                .execute()
            )
            days.append({
                "date": day_start.strftime("%b %d"),
                "messages": result.count or 0,
            })

        return days
    except Exception as exc:
        logger.error(f"messages_per_day error: {exc}")
        return []


@router.get("/messages-per-room")
async def messages_per_room(
    _: CurrentUser,
    client: Client = Depends(_get_client),
):
    """
    Return message counts grouped by room (for a bar chart).
    """
    try:
        rooms_result = client.table("rooms").select("id, name").execute()
        rooms = rooms_result.data or []

        result = []
        for room in rooms:
            count_result = (
                client.table("messages")
                .select("id", count="exact")
                .eq("room_id", room["id"])
                .execute()
            )
            result.append({
                "room": room["name"],
                "messages": count_result.count or 0,
            })

        # Sort by message count descending, take top 10
        result.sort(key=lambda x: x["messages"], reverse=True)
        return result[:10]
    except Exception as exc:
        logger.error(f"messages_per_room error: {exc}")
        return []
