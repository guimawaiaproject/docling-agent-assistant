"""
Tests de performance — temps de réponse réels.
"""

import os
import time

import pytest

pytestmark = [pytest.mark.performance, pytest.mark.slow]

SEUILS = {
    "p50_ms": 500,
    "p95_ms": 1500,
    "p99_ms": 3000,
    "n_iterations": 30,
}


def test_catalogue_response_times(http_client):
    """P50/P95/P99 sur GET /api/v1/catalogue."""
    times = []
    n = SEUILS["n_iterations"]
    for _ in range(n):
        start = time.perf_counter()
        resp = http_client.get("/api/v1/catalogue", params={"limit": 20})
        elapsed_ms = (time.perf_counter() - start) * 1000
        times.append(elapsed_ms)
        assert resp.status_code == 200

    times.sort()
    p50 = times[int(n * 0.50)]
    p95 = times[int(n * 0.95)] if n >= 20 else times[-1]
    p99 = times[int(n * 0.99)] if n >= 100 else times[-1]

    print(f"\nCatalogue (N={n}): P50={p50:.0f}ms P95={p95:.0f}ms P99={p99:.0f}ms")
    assert p50 < SEUILS["p50_ms"], f"P50 trop lent : {p50:.0f}ms"
    assert p95 < SEUILS["p95_ms"], f"P95 trop lent : {p95:.0f}ms"
    assert p99 < SEUILS["p99_ms"], f"P99 trop lent : {p99:.0f}ms"


def test_health_response_time(http_client):
    """Health check < 200ms."""
    times = []
    for _ in range(10):
        start = time.perf_counter()
        resp = http_client.get("/health")
        times.append((time.perf_counter() - start) * 1000)
        assert resp.status_code == 200
    avg = sum(times) / len(times)
    print(f"\nHealth avg: {avg:.0f}ms")
    assert avg < 200
