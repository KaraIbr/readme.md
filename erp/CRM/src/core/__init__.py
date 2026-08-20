"""Cross-cutting infrastructure for the CRM backend."""

from core.config import Settings, get_settings
from core.database import get_session
from core.logging import configure_logging, get_logger

__all__ = [
    "Settings",
    "configure_logging",
    "get_logger",
    "get_session",
    "get_settings",
]
