"""Shared application dependencies — avoids circular imports."""

from __future__ import annotations

import httpx

# Module-level shared httpx client (created/closed in lifespan)
_http_client: httpx.AsyncClient | None = None


def set_http_client(client: httpx.AsyncClient) -> None:
    """Set the shared httpx client (called during startup)."""
    global _http_client
    _http_client = client


def clear_http_client() -> None:
    """Clear the shared httpx client (called during shutdown)."""
    global _http_client
    _http_client = None


def get_http_client() -> httpx.AsyncClient:
    """Return the shared httpx AsyncClient."""
    if _http_client is None:
        raise RuntimeError("httpx client not initialized. App not started.")
    return _http_client
