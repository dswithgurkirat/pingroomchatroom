"""
PingRoom - Real-time Chat SaaS Backend
Entry point for the FastAPI application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.routes import auth, rooms, messages, stickers, payments, webhooks, stats

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("PingRoom API starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Allowed Origins: {settings.allowed_origins_list}")
    yield
    logger.info("PingRoom API shutting down...")


app = FastAPI(
    title="PingRoom API",
    description="Production-ready real-time chat SaaS backend with Supabase & Stripe",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    # IMPORTANT: Browsers reject allow_credentials=true with allow_origins="*".
    # Use explicit origins in production (set ALLOWED_ORIGINS on Render).
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/v1/auth",     tags=["Auth"])
app.include_router(rooms.router,     prefix="/api/v1/rooms",    tags=["Rooms"])
app.include_router(messages.router,  prefix="/api/v1/messages", tags=["Messages"])
app.include_router(stickers.router,  prefix="/api/v1/stickers", tags=["Stickers"])
app.include_router(payments.router,  prefix="/api/v1/payments", tags=["Payments"])
app.include_router(webhooks.router,  prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(stats.router,     prefix="/api/v1/stats",    tags=["Stats"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "PingRoom API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

