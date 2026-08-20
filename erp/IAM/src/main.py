"""FastAPI application entrypoint for IAM."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from iam.api.middleware import add_security_middleware
from iam.api.v1 import api_v1
from iam.core.config import get_settings
from iam.core.database import create_all, dispose_engine
from iam.core.exceptions import register_exception_handlers
from iam.core.logging import configure_logging
from iam.domains.auth.router import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


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
    """Create and configure the IAM FastAPI application."""

    settings = get_settings()
    configure_logging()

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
