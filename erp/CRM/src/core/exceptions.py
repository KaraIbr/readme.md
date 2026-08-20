"""Application exceptions and FastAPI exception handlers."""

from typing import Any

from core.logging import get_logger
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = get_logger(__name__)


class AppError(Exception):
    """Base exception for expected application failures."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "application_error"

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.status_code
        self.code = code or self.code
        self.details = details


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "authentication_failed"


class AuthorizationError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "authorization_failed"


class InvalidOperationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "invalid_operation"


def error_payload(
    *,
    code: str,
    message: str,
    details: Any = None,
) -> dict[str, Any]:
    """Build the API error response envelope."""

    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ),
    )


async def http_exception_handler(
    _: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(
            code="http_error",
            message=str(exc.detail),
        ),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    details = exc.errors()
    for error in details:
        context = error.get("ctx")
        if isinstance(context, dict):
            ctx_error = context.get("error")
            if isinstance(ctx_error, Exception):
                context["error"] = str(ctx_error)
            elif isinstance(ctx_error, bytes):
                context["error"] = ctx_error.decode("utf-8", errors="replace")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_payload(
            code="request_validation_error",
            message="Request validation failed",
            details=details,
        ),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_payload(
            code="internal_server_error",
            message="Internal server error",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on a FastAPI app."""

    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, unhandled_exception_handler)
