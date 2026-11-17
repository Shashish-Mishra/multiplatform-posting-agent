"""
Telegram integration.

Docs: https://core.telegram.org/bots/api#sendmessage
Setup:
  1. Create a bot via @BotFather on Telegram -> get TELEGRAM_BOT_TOKEN.
  2. Add the bot to a channel/group (or start a chat with it) and get the
     chat id (e.g. via https://api.telegram.org/bot<token>/getUpdates).
"""
import httpx

from app.config import settings
from app.platforms.base import BasePlatform


class TelegramPlatform(BasePlatform):
    name = "Telegram"

    def is_configured(self) -> bool:
        return bool(settings.telegram_bot_token and settings.telegram_chat_id)

    async def publish(self, client: httpx.AsyncClient, message: str) -> dict:
        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        payload = {"chat_id": settings.telegram_chat_id, "text": message}

        response = await client.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            raise RuntimeError(data.get("description", "Telegram API error"))

        result = data["result"]
        chat = result.get("chat", {})
        message_id = result.get("message_id")

        # Public post URL only resolvable for public channels with a username.
        username = chat.get("username")
        if username:
            posted_url = f"https://t.me/{username}/{message_id}"
            public_access = True
        else:
            posted_url = f"telegram://chat/{chat.get('id')}/{message_id}"
            public_access = False

        return {"posted_url": posted_url, "public_access": public_access}
