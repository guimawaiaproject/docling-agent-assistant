"""
Monitoring and observability module.
Sentry integration + simple in-memory metrics.
"""
import logging
import time
from functools import wraps
from typing import Optional

logger = logging.getLogger(__name__)


def init_monitoring(sentry_dsn: Optional[str] = None):
    """Initialize Sentry error tracking (if DSN provided)."""
    if sentry_dsn:
        try:
            import sentry_sdk

            sentry_sdk.init(
                dsn=sentry_dsn,
                traces_sample_rate=0.3,
                profiles_sample_rate=0.1,
                environment="production",
                release="docling-agent@2.0.0",
            )
            logger.info("Sentry monitoring initialized")
        except ImportError:
            logger.warning(
                "sentry-sdk not installed — monitoring disabled"
            )
    else:
        logger.info("No SENTRY_DSN — monitoring disabled")


class Metrics:
    """Simple in-memory metrics counter. Resets on restart."""

    _data = {
        "gemini_calls_total": 0,
        "gemini_calls_success": 0,
        "gemini_calls_failed": 0,
        "gemini_rate_limited": 0,
        "invoices_processed": 0,
        "products_added": 0,
        "products_updated": 0,
        "ocr_calls_total": 0,
        "avg_processing_time_ms": 0.0,
    }
    _processing_times: list = []

    @classmethod
    def increment(cls, key: str, value: int = 1):
        """Increment a counter metric."""
        if key in cls._data:
            cls._data[key] += value

    @classmethod
    def record_processing_time(cls, ms: float):
        """Record a processing time sample (keeps last 100)."""
        cls._processing_times.append(ms)
        cls._processing_times[:] = cls._processing_times[-100:]
        if cls._processing_times:
            avg = sum(cls._processing_times) / len(
                cls._processing_times
            )
            cls._data["avg_processing_time_ms"] = round(avg, 1)

    @classmethod
    def get_all(cls) -> dict:
        """Return all metrics as a dict."""
        return dict(cls._data)


def timed(func):
    """Decorator to measure and log function execution time."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info(
                f"{func.__name__} completed in {elapsed_ms:.0f}ms"
            )
            Metrics.record_processing_time(elapsed_ms)
            return result
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(
                f"{func.__name__} failed after {elapsed_ms:.0f}ms"
            )
            raise

    return wrapper
