"""
Slack integration (Incoming Webhook).

Docs: https://api.slack.com/messaging/webhooks
Setup:
  1. Create a Slack App -> enable "Incoming Webhooks" -> add a webhook to a
     channel -> copy the Webhook URL into SLACK_WEBHOOK_URL.
"""
import httpx

from app.config import settings
from app.platforms.base import BasePlatform


class SlackPlatform(BasePlatform):
    name = "Slack"

    def is_configured(self) -> bool:
        return bool(settings.slack_webhook_url)

    async def publish(self, client: httpx.AsyncClient, message: str) -> dict:
        payload = {"text": message}

        response = await client.post(
            settings.slack_webhook_url, json=payload, timeout=self.timeout
        )
        response.raise_for_status()

        if response.text.strip().lower() != "ok":
            raise RuntimeError(f"Slack webhook returned unexpected body: {response.text}")

        # Incoming webhooks do not return a message permalink, so we point to
        # the workspace's channel the webhook is bound to (best effort).
        return {"posted_url": settings.slack_webhook_url, "public_access": False}
