"""
Stripe webhook endpoint.

Stripe signs every event with STRIPE_WEBHOOK_SECRET.
This endpoint verifies the signature before processing.
"""

import logging

import stripe as stripe_lib
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.supabase import get_supabase_admin
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)
router = APIRouter()


def _payment_service() -> PaymentService:
    # Use the admin client here so the insert bypasses RLS
    return PaymentService(get_supabase_admin())


@router.post("/stripe", status_code=200)
async def stripe_webhook(
    request: Request,
    service: PaymentService = Depends(_payment_service),
):
    """
    Receive and process Stripe events.

    Handled events:
      - checkout.session.completed  → record purchase in DB
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe_lib.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe_lib.errors.SignatureVerificationError:
        logger.warning("Stripe webhook signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )
    except Exception as exc:
        logger.error(f"Webhook parse error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed webhook payload",
        )

    event_type = event["type"]
    logger.info(f"Stripe event received: {event_type} | id={event['id']}")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]

        # Only record paid sessions
        if session.get("payment_status") != "paid":
            logger.info(f"Session {session['id']} not yet paid — skipping")
            return JSONResponse({"received": True})

        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        sticker_id = metadata.get("sticker_id")
        payment_id = session.get("payment_intent") or session["id"]

        if not user_id or not sticker_id:
            logger.error(f"Missing metadata in session {session['id']}: {metadata}")
            return JSONResponse({"received": True})

        await service.record_purchase(
            user_id=user_id,
            sticker_id=sticker_id,
            payment_id=payment_id,
        )
        logger.info(f"Purchase recorded via webhook: user={user_id} sticker={sticker_id}")

    else:
        logger.debug(f"Unhandled Stripe event type: {event_type}")

    return JSONResponse({"received": True})
