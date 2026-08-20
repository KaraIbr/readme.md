"""IAM API v1 router aggregation."""

from fastapi import APIRouter

from iam.domains.auth.router import router as auth_router
from iam.domains.permissions.router import router as permissions_router
from iam.domains.services.router import router as services_router
from iam.domains.users.router import router as users_router

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth_router, prefix="/auth", tags=["auth"])
api_v1.include_router(users_router, prefix="/users", tags=["users"])
api_v1.include_router(permissions_router, prefix="/permissions", tags=["permissions"])
api_v1.include_router(services_router, prefix="/services", tags=["services"])
