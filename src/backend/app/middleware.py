"""Rate-limiting middleware using a sliding-window counter per client IP."""

from __future__ import annotations

import ipaddress
import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

_DEFAULT_TRUSTED_PROXIES = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]


def _is_trusted_proxy(ip: str, trusted: list[ipaddress.IPv4Network | ipaddress.IPv6Network]) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return any(addr in net for net in trusted)
    except ValueError:
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter per client IP."""

    EXEMPT_PATHS = {"/api/health"}
    _CLEANUP_INTERVAL = 1000
    _MAX_TRACKED_IPS = 10_000

    def __init__(self, app, requests_per_minute: int = 30):
        super().__init__(app)
        self._rpm = requests_per_minute
        self._window = 60.0
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._request_count = 0

    def _resolve_client_ip(self, request: Request) -> str:
        direct_ip = request.client.host if request.client else "unknown"
        if direct_ip == "unknown":
            return direct_ip
        if _is_trusted_proxy(direct_ip, _DEFAULT_TRUSTED_PROXIES):
            forwarded = request.headers.get("x-forwarded-for", "")
            if forwarded:
                real_ip = forwarded.split(",")[0].strip()
                if real_ip:
                    return real_ip
        return direct_ip

    def _sweep_stale_ips(self, cutoff: float) -> None:
        stale_keys = [ip for ip, ts in self._hits.items() if not ts or ts[-1] <= cutoff]
        for key in stale_keys:
            del self._hits[key]

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_ip = self._resolve_client_ip(request)
        now = time.monotonic()
        cutoff = now - self._window

        self._request_count += 1
        if self._request_count >= self._CLEANUP_INTERVAL or len(self._hits) > self._MAX_TRACKED_IPS:
            self._sweep_stale_ips(cutoff)
            self._request_count = 0

        timestamps = self._hits[client_ip]
        self._hits[client_ip] = [t for t in timestamps if t > cutoff]

        if len(self._hits[client_ip]) >= self._rpm:
            retry_after = int(self._window - (now - self._hits[client_ip][0])) + 1
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": str(retry_after)},
            )

        self._hits[client_ip].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self._rpm)
        response.headers["X-RateLimit-Remaining"] = str(
            self._rpm - len(self._hits[client_ip])
        )
        return response
