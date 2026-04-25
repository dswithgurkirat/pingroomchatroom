"""
JWT authentication dependency for FastAPI routes.

Validates Bearer tokens issued by Supabase Auth using the project's JWT secret.
"""

import logging
from typing import Annotated

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    """
    Supabase can issue JWTs signed with asymmetric keys (e.g. ES256/RS256).
    In that case we must validate using the project's JWKS endpoint.
    """
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


class AuthenticatedUser:
    """Represents the currently authenticated user extracted from JWT payload."""

    def __init__(self, user_id: str, email: str, role: str = "authenticated"):
        self.user_id = user_id
        self.email = email
        self.role = role

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AuthenticatedUser user_id={self.user_id} email={self.email}>"


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> AuthenticatedUser:
    """
    FastAPI dependency that validates a Supabase JWT and returns the user.

    Usage:
        @router.get("/protected")
        async def protected(user: CurrentUser):
            ...
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        header = jwt.get_unverified_header(token)
        logger.info(f"JWT Header: {header}")

        alg = header.get("alg", "HS256")
        if alg == "HS256":
            key = settings.SUPABASE_JWT_SECRET
        else:
            # ES256/RS256/etc: use JWKS signing key
            key = _get_jwks_client().get_signing_key_from_jwt(token).key

        payload = jwt.decode(
            token,
            key,
            algorithms=[alg],
            options={"verify_aud": False},  # Supabase omits "aud" in some configs
            leeway=300,  # tolerate small clock skew (iat/nbf)
        )

        user_id: str = payload.get("sub")
        email: str = payload.get("email", "")
        role: str = payload.get("role", "authenticated")

        if user_id is None:
            logger.warning("JWT missing 'sub' claim")
            raise credentials_exception

        logger.debug(f"Authenticated user: {user_id}")
        return AuthenticatedUser(user_id=user_id, email=email, role=role)

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        logger.warning(f"Invalid JWT token: {exc}")
        raise credentials_exception


# Convenient type alias for dependency injection
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
