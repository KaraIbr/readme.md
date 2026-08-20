"""Serialization helpers for agent tool outputs."""

import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any


def normalize_value(value: Any) -> Any:
    """Convert Python/domain values to JSON-safe values."""

    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list | tuple):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_value(item) for key, item in value.items()}
    return value


def to_json(data: dict[str, Any]) -> str:
    """Serialize structured tool data for model-readable tool messages."""

    return json.dumps(normalize_value(data), ensure_ascii=False, sort_keys=True)
