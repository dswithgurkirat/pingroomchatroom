"""
Payment routes — Stripe checkout session creation & purchase status.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.supabase import get_supabase_client
from app.middleware.auth import CurrentUser
from app.models.schemas import CheckoutSessionRequest, CheckoutSessionResponse
from app.services.payment_service import PaymentService

router = APIRouter()


def _payment_service() -> PaymentService:
    return PaymentService(get_supabase_client())


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    data: CheckoutSessionRequest,
    current_user: CurrentUser,
    service: PaymentService = Depends(_payment_service),
):
    """
    Generate a Stripe Checkout session for purchasing a sticker.
    Redirect the user to the returned `checkout_url`.
    """
    return await service.create_checkout_session(data.sticker_id, current_user.user_id)


@router.get("/verify/{sticker_id}")
async def verify_purchase(
    sticker_id: UUID,
    current_user: CurrentUser,
    service: PaymentService = Depends(_payment_service),
):
    """Check whether the current user owns a particular sticker."""
    owned = await service.verify_purchase(current_user.user_id, sticker_id)
    return {"sticker_id": str(sticker_id), "owned": owned}
