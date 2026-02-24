# ═══════════════════════════════════════
# Stage 1: Builder — install dependencies
# ═══════════════════════════════════════
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ═══════════════════════════════════════
# Stage 2: Runtime — minimal production image (~120MB)
# ═══════════════════════════════════════
FROM python:3.11-slim AS runtime

# Security: non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code only (no tests, no docs, no secrets)
COPY backend/ ./backend/
COPY app.py .
COPY api.py .

# Permissions
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthchecks are defined dynamically in docker-compose.yml

# Production: FastAPI via Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
