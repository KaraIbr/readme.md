from core.exceptions import NotFoundError, register_exception_handlers
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, model_validator


def test_app_error_handler_returns_error_envelope() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/missing")
    async def missing() -> None:
        raise NotFoundError("Contact not found", details={"contact_id": 123})

    client = TestClient(app)
    response = client.get("/missing")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "Contact not found",
            "details": {"contact_id": 123},
        },
    }


def test_validation_handler_serializes_value_error_context() -> None:
    class Payload(BaseModel):
        value: str

        @model_validator(mode="after")
        def reject_value(self) -> Payload:
            raise ValueError("Invalid payload")

    app = FastAPI()
    register_exception_handlers(app)

    @app.post("/payload")
    async def create_payload(_: Payload) -> None:
        return None

    client = TestClient(app)
    response = client.post("/payload", json={"value": "bad"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "request_validation_error"
    assert response.json()["error"]["details"][0]["ctx"]["error"] == "Invalid payload"
