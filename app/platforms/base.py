"""Base class every platform integration must implement."""
from abc import ABC, abstractmethod
from datetime import datetime

import httpx

from app.schemas import PlatformResult


class BasePlatform(ABC):
    """Common interface for all third-party platform integrations."""

    #: Human readable platform name shown in the API response.
    name: str = "BasePlatform"

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if the required credentials/env vars are present."""
        raise NotImplementedError

    @abstractmethod
    async def publish(self, client: httpx.AsyncClient, message: str) -> dict:
        """
        Publish the message to the platform.

        Must return a dict with keys:
            posted_url (str), public_access (bool)

        Raise any Exception on failure - it will be captured by `post()`.
        """
        raise NotImplementedError

    async def post(self, client: httpx.AsyncClient, message: str) -> PlatformResult:
        """Template method that wraps `publish()` with timing + error handling."""
        if not self.is_configured():
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="Platform not configured (missing credentials).",
            )

        try:
            result = await self.publish(client, message)
            now = datetime.now()
            return PlatformResult(
                platform=self.name,
                status="success",
                posted_url=result.get("posted_url"),
                public_access=result.get("public_access", True),
                date=now.strftime("%Y-%m-%d"),
                time=now.strftime("%H:%M:%S"),
                error=None,
            )
        except Exception as exc:  # noqa: BLE001 - we want to capture *any* failure
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error=str(exc),
            )
