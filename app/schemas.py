"""Pydantic request/response schemas."""
import re
from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# Matches a single http/https URL inside the message text.
_URL_PATTERN = re.compile(
    r"(https?://[^\s]+)",
    re.IGNORECASE,
)


class PostRequest(BaseModel):
    message: str = Field(..., description="Message to post, must contain exactly one CTA link.")

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message must not be empty.")

        if len(value) > 200:
            raise ValueError(f"Message must not exceed 200 characters (got {len(value)}).")

        urls = _URL_PATTERN.findall(value)

        if len(urls) == 0:
            raise ValueError("Message must contain exactly one CTA link (none found).")

        if len(urls) > 1:
            raise ValueError(f"Message must contain exactly one CTA link (found {len(urls)}).")

        url = urls[0].rstrip(").,;!?")
        if not cls._is_valid_url(url):
            raise ValueError(f"The CTA link '{url}' is not a valid URL.")

        return value

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        pattern = re.compile(
            r"^https?://"
            r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
            r"[a-zA-Z]{2,}"
            r"(?::\d+)?"
            r"(?:/[^\s]*)?$"
        )
        return bool(pattern.match(url))


class PlatformResult(BaseModel):
    platform: str
    status: str  # "success" | "failed"
    posted_url: Optional[str] = None
    public_access: bool = False
    date: Optional[str] = None
    time: Optional[str] = None
    error: Optional[str] = None


class PostResponse(BaseModel):
    success: bool
    results: List[PlatformResult]
