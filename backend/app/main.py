"""
Notre Histoire — FastAPI application entry point.
Assembles all routers, middleware, CORS, and startup logic.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, couple, media, music, dates, quotes, admin

logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("notre_histoire")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("🚀 Notre Histoire API démarrage...")
    # Ensure media directories exist
    import os
    from pathlib import Path
    for folder in ("photos", "videos", "music"):
        Path(settings.MEDIA_ROOT, folder).mkdir(parents=True, exist_ok=True)

    yield

    logger.info("🛑 Notre Histoire API arrêt.")


app = FastAPI(
    title="Notre Histoire API",
    description="Backend de l'application de souvenirs en couple 'Notre Histoire'.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX)
app.include_router(couple.router, prefix=PREFIX)
app.include_router(media.router, prefix=PREFIX)
app.include_router(music.router, prefix=PREFIX)
app.include_router(dates.router, prefix=PREFIX)
app.include_router(quotes.router, prefix=PREFIX)
app.include_router(admin.router, prefix=PREFIX)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Santé"])
async def health():
    return {"status": "ok", "version": "1.0.0", "environment": settings.ENVIRONMENT}