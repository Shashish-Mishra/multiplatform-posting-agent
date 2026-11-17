"""
GitHub Gist integration.

Docs: https://docs.github.com/en/rest/gists/gists#create-a-gist
Setup:
  1. Create a Personal Access Token (classic) with the "gist" scope at
     https://github.com/settings/tokens -> copy into GITHUB_TOKEN.
  2. Set GITHUB_USERNAME to your GitHub username (used for display only).
"""
from datetime import datetime

import httpx

from app.config import settings
from app.platforms.base import BasePlatform


class GitHubGistPlatform(BasePlatform):
    name = "GitHub Gist"

    def is_configured(self) -> bool:
        return bool(settings.github_token)

    async def publish(self, client: httpx.AsyncClient, message: str) -> dict:
        url = "https://api.github.com/gists"
        headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
        }
        filename = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        payload = {
            "description": "Automated multi-platform post",
            "public": True,
            "files": {filename: {"content": message}},
        }

        response = await client.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        return {
            "posted_url": data.get("html_url"),
            "public_access": data.get("public", False),
        }
