"""
Discord integration (Incoming Webhook).

Docs: https://discord.com/developers/docs/resources/webhook#execute-webhook
Setup:
  1. In a Discord server -> Channel Settings -> Integrations -> Webhooks ->
     New Webhook -> copy the Webhook URL into DISCORD_WEBHOOK_URL.
"""
import httpx

from app.config import settings
from app.platforms.base import BasePlatform


class DiscordPlatform(BasePlatform):
    name = "Discord"

    def is_configured(self) -> bool:
        return bool(settings.discord_webhook_url)

    async def publish(self, client: httpx.AsyncClient, message: str) -> dict:
        # ?wait=true makes Discord return the created message object (with id).
        url = f"{settings.discord_webhook_url}?wait=true"
        payload = {"content": message}

        response = await client.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        message_id = data.get("id")
        channel_id = data.get("channel_id")

        # Webhook response does not include guild_id; construct a best-effort
        # jump-link that works once Discord resolves it client-side.
        posted_url = f"https://discord.com/channels/@me/{channel_id}/{message_id}"

        return {"posted_url": posted_url, "public_access": True}
