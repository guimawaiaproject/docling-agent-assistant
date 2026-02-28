"""Shared serialization utilities for asyncpg Record → JSON-safe dict."""

from datetime import date, datetime
from decimal import Decimal


def _serialize_val(v):
    """Convert date/datetime to ISO strings, Decimal to float. Returns JSON-safe value."""
    if v is None:
        return v
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    if hasattr(v, "isoformat"):
        return v.isoformat()
    if hasattr(v, "__float__") and not isinstance(v, (int, float, bool)):
        return float(v)
    return v


def serialize_row(row: dict) -> dict:
    """Return a COPY with date/datetime as ISO strings, Decimal as float. Does not mutate in-place."""
    return {k: _serialize_val(v) for k, v in (row or {}).items()}
