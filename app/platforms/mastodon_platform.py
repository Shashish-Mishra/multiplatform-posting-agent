"""
Mastodon integration.

Docs: https://docs.joinmastodon.org/methods/statuses/#create
Setup:
  1. On your Mastodon instance -> Preferences -> Development -> New
     Application -> grant "write:statuses" scope -> copy the access token
     into MASTODON_ACCESS_TOKEN and set MASTODON_INSTANCE_URL (e.g.
     https://mastodon.social).
"""
import httpx

from app.config import settings
from app.platforms.base import BasePlatform


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    def is_configured(self) -> bool:
        return bool(settings.mastodon_access_token and settings.mastodon_instance_url)

    async def publish(self, client: httpx.AsyncClient, message: str) -> dict:
        url = f"{settings.mastodon_instance_url.rstrip('/')}/api/v1/statuses"
        headers = {"Authorization": f"Bearer {settings.mastodon_access_token}"}
        payload = {"status": message, "visibility": "public"}

        response = await client.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        posted_url = data.get("url")
        visibility = data.get("visibility")

        return {"posted_url": posted_url, "public_access": visibility == "public"}
