"""
Stripe client initialisation.
"""

import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_stripe() -> stripe:
    """Return the configured Stripe module."""
    return stripe
