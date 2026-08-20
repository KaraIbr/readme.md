"""No CRM user endpoints.

IAM owns user creation, login, refresh, IAM permissions, and service-access
administration. CRM keeps this module only for read-side IAM user references.
"""

from fastapi import APIRouter

router = APIRouter()
