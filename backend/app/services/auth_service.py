"""
Authentication service — wraps Supabase Auth operations.
"""

import logging

from fastapi import HTTPException, status
from supabase import Client

from app.models.schemas import SignUpRequest, SignInRequest, AuthResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, client: Client):
        self.client = client

    async def sign_up(self, data: SignUpRequest) -> AuthResponse:
        try:
            response = self.client.auth.sign_up(
                {
                    "email": data.email,
                    "password": data.password,
                    "options": {
                        "data": {"full_name": data.full_name or ""}
                    },
                }
            )
            if response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed. Check your email for a confirmation link.",
                )
            logger.info(f"New user registered: {response.user.id}")
            return AuthResponse(
                access_token=response.session.access_token if response.session else "",
                user_id=str(response.user.id),
                email=response.user.email,
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Sign-up error: {exc}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

    async def sign_in(self, data: SignInRequest) -> AuthResponse:
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": data.email, "password": data.password}
            )
            logger.info(f"User signed in: {response.user.id}")
            return AuthResponse(
                access_token=response.session.access_token,
                user_id=str(response.user.id),
                email=response.user.email,
            )
        except Exception as exc:
            logger.warning(f"Sign-in failed for {data.email}: {exc}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

    async def sign_out(self, token: str) -> None:
        try:
            self.client.auth.sign_out()
            logger.info("User signed out")
        except Exception as exc:
            logger.warning(f"Sign-out error (non-critical): {exc}")
