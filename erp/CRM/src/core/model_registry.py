"""Model import registry for SQLModel metadata operations."""

from importlib import import_module

MODEL_MODULES = (
    "domains.users.models",
    "domains.contacts.models",
    "domains.leads.models",
    "domains.proposals.models",
    "domains.activities.models",
    "domains.opportunities.models",
    "domains.technical_visits.models",
    "domains.permissions.models",
    "domains.pipeline.models",
)


def import_model_modules() -> None:
    """Import all persisted models so SQLModel.metadata is complete."""

    for module_name in MODEL_MODULES:
        import_module(module_name)
