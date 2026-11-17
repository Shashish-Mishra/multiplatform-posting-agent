"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Discord
    discord_webhook_url: str = ""

    # Slack
    slack_webhook_url: str = ""

    # Mastodon
    mastodon_instance_url: str = "https://mastodon.social"
    mastodon_access_token: str = ""

    # GitHub Gist
    github_token: str = ""
    github_username: str = ""

    # App
    max_message_length: int = 200
    request_timeout_seconds: float = 10.0


settings = Settings()
