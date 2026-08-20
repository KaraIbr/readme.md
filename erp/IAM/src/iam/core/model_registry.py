"""Model import registry for SQLModel metadata operations."""

from importlib import import_module

MODEL_MODULES = (
    "iam.domains.users.models",
    "iam.domains.auth.models",
    "iam.domains.permissions.models",
    "iam.domains.services.models",
)


def import_model_modules() -> None:
    """Import all persisted models so SQLModel metadata is complete."""

    for module_name in MODEL_MODULES:
        import_module(module_name)
