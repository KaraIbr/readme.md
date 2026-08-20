"""Unit coverage for IAM security response middleware."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient
from iam.api.middleware import SecurityHeadersMiddleware, add_security_middleware

EXPECTED_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "strict-transport-security": "max-age=31536000; includeSubDomains",
    "referrer-policy": "strict-origin-when-cross-origin",
    "permissions-policy": "geolocation=(), microphone=(), camera=()",
    "content-security-policy": (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    ),
}


def test_add_security_middleware_registers_middleware() -> None:
    app = FastAPI()
    add_security_middleware(app)
    middleware_classes = [middleware.cls for middleware in app.user_middleware]
    assert SecurityHeadersMiddleware in middleware_classes


async def test_security_headers_are_added_to_every_response() -> None:
    app = FastAPI()
    add_security_middleware(app)

    @app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse({"ok": True})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    for header, expected in EXPECTED_HEADERS.items():
        assert response.headers.get(header) == expected


async def test_security_headers_cover_error_responses() -> None:
    app = FastAPI()
    add_security_middleware(app)

    @app.get("/missing")
    async def missing() -> JSONResponse:
        raise HTTPException(status_code=404, detail="nope")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/missing")

    assert response.status_code == 404
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
