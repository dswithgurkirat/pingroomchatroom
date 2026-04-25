"""
Payment service — Stripe checkout sessions & purchase recording.
"""

import logging
from uuid import UUID

import stripe as stripe_lib
from fastapi import HTTPException
from supabase import Client

from app.core.config import settings
from app.models.schemas import CheckoutSessionResponse, PurchaseResponse
from app.services.sticker_service import StickerService

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, client: Client):
        self.client = client
        self.sticker_service = StickerService(client)

    async def create_checkout_session(
        self, sticker_id: UUID, user_id: str
    ) -> CheckoutSessionResponse:
        """Create a Stripe Checkout session for a sticker purchase."""
        sticker = await self.sticker_service.get_sticker(sticker_id)

        try:
            session = stripe_lib.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(sticker.price * 100),  # cents
                            "product_data": {
                                "name": sticker.name,
                                "images": [sticker.url],
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{settings.FRONTEND_URL}/stickers?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/stickers?payment=cancelled",
                metadata={
                    "user_id": user_id,
                    "sticker_id": str(sticker_id),
                },
            )
            logger.info(f"Stripe session created: {session.id} for user {user_id}")
            return CheckoutSessionResponse(
                checkout_url=session.url,
                session_id=session.id,
            )
        except stripe_lib.StripeError as exc:
            logger.error(f"Stripe error: {exc}")
            raise HTTPException(status_code=502, detail=f"Payment provider error: {exc.user_message}")

    async def record_purchase(
        self, user_id: str, sticker_id: str, payment_id: str
    ) -> PurchaseResponse:
        """Persist a confirmed purchase to the database."""
        # Prevent duplicate purchases for the same payment
        existing = (
            self.client.table("purchases")
            .select("id")
            .eq("payment_id", payment_id)
            .execute()
        )
        if existing.data:
            logger.info(f"Purchase already recorded for payment {payment_id}")
            row = existing.data[0]
            result = (
                self.client.table("purchases")
                .select("*")
                .eq("id", row["id"])
                .single()
                .execute()
            )
            return PurchaseResponse(**result.data)

        try:
            result = (
                self.client.table("purchases")
                .insert(
                    {
                        "user_id": user_id,
                        "sticker_id": sticker_id,
                        "payment_id": payment_id,
                    }
                )
                .execute()
            )
            if not result.data:
                raise Exception("Insert returned no data")

            logger.info(f"Purchase recorded: user={user_id} sticker={sticker_id} payment={payment_id}")
            return PurchaseResponse(**result.data[0])
        except Exception as exc:
            logger.error(f"record_purchase error: {exc}")
            raise HTTPException(status_code=500, detail="Could not record purchase")

    async def verify_purchase(self, user_id: str, sticker_id: UUID) -> bool:
        """Check whether a user has already purchased a sticker."""
        result = (
            self.client.table("purchases")
            .select("id")
            .eq("user_id", user_id)
            .eq("sticker_id", str(sticker_id))
            .execute()
        )
        return bool(result.data)
