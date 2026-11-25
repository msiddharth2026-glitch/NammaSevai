"""
Security and Reliability Middlewares for NammaSevai AI / BharatSevai AI.
Includes:
  1. SecurityHeadersMiddleware (HSTS, CSP, X-Frame-Options, NoSniff, XSS)
  2. RateLimitingMiddleware (Sliding-window IP throttling with test/local exemptions)
  3. RequestSizeLimitMiddleware (Payload DOS protection)
"""

import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger("nammasevai.security_middleware")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects hardened HTTP security headers on all server responses.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Clickjacking defense
        response.headers["X-Frame-Options"] = "DENY"
        
        # Legacy browser XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer control
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Hardware permissions restriction (only microphone is permitted for voice queries)
        response.headers["Permissions-Policy"] = "microphone=(self), camera=(), geolocation=(), payment=()"
        
        # HSTS (Strict-Transport-Security) for production HTTPS enforcement
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class RateLimiter:
    """
    Sliding window in-memory rate limiter per IP address.
    """
    def __init__(self):
        self._requests = defaultdict(list)

    def is_allowed(self, client_ip: str, limit: int, window_seconds: int = 60) -> bool:
        now = time.time()
        # Clean older requests outside the window
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] 
            if now - ts < window_seconds
        ]
        
        if len(self._requests[client_ip]) >= limit:
            return False
            
        self._requests[client_ip].append(now)
        return True

_rate_limiter = RateLimiter()

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Protects API endpoints against brute force, denial of service, and scraping.
    Whitelists local loopback/test clients for full test performance.
    """
    def __init__(self, app, requests_per_minute: int = 120, match_requests_per_minute: int = 60, admin_requests_per_minute: int = 40):
        super().__init__(app)
        self.general_limit = requests_per_minute
        self.match_limit = match_requests_per_minute
        self.admin_limit = admin_requests_per_minute

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "127.0.0.1"

        # Local test suite & loopback bypass so unit tests run at in-memory speed
        if client_ip in ("127.0.0.1", "::1", "testclient", "localhost"):
            return await call_next(request)

        path = request.url.path

        # Determine rate limit threshold based on endpoint sensitivity
        if path.startswith("/api/assistant/match"):
            limit = self.match_limit
        elif path.startswith("/api/admin"):
            limit = self.admin_limit
        else:
            limit = self.general_limit

        if not _rate_limiter.is_allowed(client_ip, limit, window_seconds=60):
            logger.warning(f"RATE LIMIT EXCEEDED: IP {client_ip} throttled on {path}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please wait a moment before sending additional requests.",
                    "retry_after_seconds": 60
                },
                headers={"Retry-After": "60"}
            )

        return await call_next(request)

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Rejects oversized payloads to protect against memory exhaustion DOS.
    Allows up to 20MB for bulk admin scheme import, 5MB for all other requests.
    """
    def __init__(self, app, max_upload_bytes: int = 5 * 1024 * 1024, max_body_bytes: int = None):
        super().__init__(app)
        self.max_bytes = max_body_bytes if max_body_bytes is not None else max_upload_bytes
        self.admin_import_max_bytes = 20 * 1024 * 1024

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                max_allowed = self.admin_import_max_bytes if request.url.path == "/api/admin/schemes/import" else self.max_bytes
                if length > max_allowed:
                    logger.warning(f"PAYLOAD TOO LARGE: Request to {request.url.path} with size {length} bytes rejected.")
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Payload Too Large",
                            "message": f"Request body exceeds maximum allowed size ({max_allowed // (1024 * 1024)}MB)."
                        }
                    )
            except ValueError:
                pass

        return await call_next(request)
