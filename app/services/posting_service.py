"""Orchestrates posting a message to all configured platforms concurrently."""
import asyncio
from typing import List

import httpx

from app.config import settings
from app.platforms import (
    DiscordPlatform,
    GitHubGistPlatform,
    MastodonPlatform,
    SlackPlatform,
    TelegramPlatform,
)
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult, PostResponse

# Register every supported platform here. Adding a new platform only
# requires creating a class in app/platforms/ and listing it below.
PLATFORMS: List[BasePlatform] = [
    TelegramPlatform(timeout=settings.request_timeout_seconds),
    DiscordPlatform(timeout=settings.request_timeout_seconds),
    SlackPlatform(timeout=settings.request_timeout_seconds),
    MastodonPlatform(timeout=settings.request_timeout_seconds),
    GitHubGistPlatform(timeout=settings.request_timeout_seconds),
]


class PostingService:
    """Publishes a message to every registered platform independently."""

    def __init__(self, platforms: List[BasePlatform] | None = None) -> None:
        self.platforms = platforms if platforms is not None else PLATFORMS

    async def publish_everywhere(self, message: str) -> PostResponse:
        async with httpx.AsyncClient() as client:
            # Each platform's failure is isolated inside BasePlatform.post(),
            # so one failing integration never blocks the others.
            tasks = [platform.post(client, message) for platform in self.platforms]
            results: List[PlatformResult] = await asyncio.gather(*tasks)

        overall_success = any(result.status == "success" for result in results)

        return PostResponse(success=overall_success, results=results)


posting_service = PostingService()
