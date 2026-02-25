"""Shared serialization utilities for asyncpg Record → JSON-safe dict."""

from decimal import Decimal
from datetime import date, datetime


def serialize_row(row: dict) -> dict:
    """Convert date/datetime to ISO strings, Decimal to float in-place."""
    for k, v in row.items():
        if isinstance(v, (datetime, date)):
            row[k] = v.isoformat()
        elif isinstance(v, Decimal):
            row[k] = float(v)
        elif hasattr(v, "isoformat"):
            row[k] = v.isoformat()
        elif hasattr(v, "__float__") and not isinstance(v, (int, float, bool)):
            row[k] = float(v)
    return row
