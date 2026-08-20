"""FastAPI application entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from api.middleware import add_security_middleware
from api.v1 import api_v1
from core.config import get_settings
from core.database import create_all, dispose_engine
from core.exceptions import register_exception_handlers
from core.logging import configure_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage local development database bootstrap and cleanup."""

    settings = get_settings()
    if settings.is_development:
        await create_all()

    try:
        yield
    finally:
        await dispose_engine()


def create_app() -> FastAPI:
    """Create and configure the CRM FastAPI application."""

    settings = get_settings()
    configure_logging()

    if settings.dev_bootstrap_enabled and not settings.is_development:
        raise RuntimeError("DEV_BOOTSTRAP_ENABLED=true is not allowed outside development")

    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    register_exception_handlers(app)
    add_security_middleware(app)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.include_router(api_v1)
    return app


app = create_app()
