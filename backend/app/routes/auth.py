"""
Authentication routes — sign up, sign in, sign out, me.
"""

from fastapi import APIRouter, Depends

from app.core.supabase import get_supabase_client
from app.middleware.auth import CurrentUser
from app.models.schemas import SignUpRequest, SignInRequest, AuthResponse, SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter()


def _auth_service() -> AuthService:
    return AuthService(get_supabase_client())


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def sign_up(
    data: SignUpRequest,
    service: AuthService = Depends(_auth_service),
):
    """Register a new user account."""
    return await service.sign_up(data)


@router.post("/signin", response_model=AuthResponse)
async def sign_in(
    data: SignInRequest,
    service: AuthService = Depends(_auth_service),
):
    """Authenticate with email + password and receive a JWT."""
    return await service.sign_in(data)


@router.post("/signout", response_model=SuccessResponse)
async def sign_out(
    current_user: CurrentUser,
    service: AuthService = Depends(_auth_service),
):
    """Invalidate the current session."""
    await service.sign_out(token="")  # Supabase tracks sessions server-side
    return SuccessResponse(message="Signed out successfully")


@router.get("/me")
async def get_me(current_user: CurrentUser):
    """Return the currently authenticated user's info."""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
    }
