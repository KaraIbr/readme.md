"""Unit coverage for IAM application exceptions and handlers."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient
from iam.core.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    InvalidOperationError,
    NotFoundError,
    app_error_handler,
    error_payload,
    http_exception_handler,
    register_exception_handlers,
    unhandled_exception_handler,
    validation_exception_handler,
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request


def test_error_payload_with_and_without_details() -> None:
    assert error_payload(code="conflict", message="Taken") == {
        "error": {"code": "conflict", "message": "Taken"},
    }
    assert error_payload(code="conflict", message="Taken", details={"email": "x"}) == {
        "error": {"code": "conflict", "message": "Taken", "details": {"email": "x"}},
    }


def test_app_error_defaults_and_overrides() -> None:
    error = AppError("boom")
    assert error.message == "boom"
    assert error.status_code == 400
    assert error.code == "application_error"
    assert error.details is None

    custom = AppError(
        "teapot",
        status_code=418,
        code="im_a_teapot",
        details={"pot": True},
    )
    assert custom.status_code == 418
    assert custom.code == "im_a_teapot"
    assert custom.details == {"pot": True}


def test_error_subclass_status_codes() -> None:
    assert NotFoundError("n").status_code == 404
    assert NotFoundError("n").code == "not_found"
    assert ConflictError("n").status_code == 409
    assert ConflictError("n").code == "conflict"
    assert AuthenticationError("n").status_code == 401
    assert AuthenticationError("n").code == "authentication_failed"
    assert AuthorizationError("n").status_code == 403
    assert AuthorizationError("n").code == "authorization_failed"
    assert InvalidOperationError("n").status_code == 422
    assert InvalidOperationError("n").code == "invalid_operation"


async def test_app_error_handler_payload() -> None:
    response = await app_error_handler(None, ConflictError("Email taken"))
    assert response.status_code == 409
    assert response.body  # JSONResponse carries the serialized envelope
    assert response.headers["content-type"] == "application/json"


async def test_http_exception_handler_with_headers() -> None:
    exc = StarletteHTTPException(
        status_code=429,
        detail="Slow down",
        headers={"Retry-After": "60"},
    )
    response = await http_exception_handler(None, exc)
    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"


def _scope() -> dict[str, object]:
    return {"type": "http", "method": "GET", "path": "/boom", "headers": []}


async def test_validation_exception_handler_serializes_ctx_errors() -> None:
    exc = RequestValidationError(
        errors=[
            {
                "loc": ("body", "email"),
                "msg": "invalid",
                "type": "value_error",
                "ctx": {"error": ValueError("not an email")},
            },
            {
                "loc": ("body", "blob"),
                "msg": "invalid",
                "type": "value_error",
                "ctx": {"error": b"\xffraw"},
            },
        ]
    )
    response = await validation_exception_handler(None, exc)
    assert response.status_code == 422
    details = response.body
    assert b"request_validation_error" in details
    assert b"not an email" in details
    assert b"raw" in details


async def test_unhandled_exception_handler_returns_500_envelope() -> None:
    request = Request(_scope())
    response = await unhandled_exception_handler(request, RuntimeError("boom"))
    assert response.status_code == 500
    assert b"internal_server_error" in response.body


async def test_register_exception_handlers_covers_errors_end_to_end() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom() -> JSONResponse:
        raise RuntimeError("boom")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/boom")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_server_error"
