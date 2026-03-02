# Docling API — Docker (uv 2026)
# Build: docker build -t docling-api .
# Run:   docker run -p 8000:8000 --env-file .env docling-api

FROM python:3.11-slim AS builder
WORKDIR /build
# Install uv (10-100x faster than pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.11-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser
WORKDIR /app
# Copy venv from builder
COPY --from=builder /build/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY apps/api/ ./apps/api/
COPY .env.example .env
RUN chown -R appuser:appuser /app
USER appuser
WORKDIR /app/apps/api
ENV PYTHONPATH=/app/apps/api
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
