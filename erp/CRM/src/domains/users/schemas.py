"""Read-only IAM user DTOs used internally by CRM."""

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    """Public IAM user reference shape."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None
    is_active: bool
