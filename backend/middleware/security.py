"""
Security middleware for FastAPI.
API Key authentication + Rate limiting.
"""
import os
import time
import logging
from collections import defaultdict

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

VALID_API_KEYS = set(os.getenv("API_KEYS", "").split(",")) - {""}


class APIKeyMiddleware(BaseHTTPMiddleware):
    EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):
        if not VALID_API_KEYS:
            return await call_next(request)
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in VALID_API_KEYS:
            logger.warning(f"Unauthorized: {request.client.host} -> {request.url.path}")
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 30, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self._requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_id = request.headers.get("X-API-Key", request.client.host)
        now = time.time()
        self._requests[client_id] = [
            t for t in self._requests[client_id] if t > now - self.window
        ]
        if len(self._requests[client_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_id}")
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded ({self.max_requests} req/{self.window}s)"},
                headers={"Retry-After": str(self.window)},
            )
        self._requests[client_id].append(now)
        return await call_next(request)
