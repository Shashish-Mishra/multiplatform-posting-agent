"""Tests for the /posting endpoint: input validation + multi-platform posting."""
import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.platforms.base import BasePlatform
from app.services.posting_service import PostingService

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fake platforms used to test orchestration without hitting real network APIs
# ---------------------------------------------------------------------------
class FakeSuccessPlatform(BasePlatform):
    name = "FakeSuccess"

    def is_configured(self) -> bool:
        return True

    async def publish(self, client: httpx.AsyncClient, message: str) -> dict:
        return {"posted_url": "https://fake.example.com/post/1", "public_access": True}


class FakeFailurePlatform(BasePlatform):
    name = "FakeFailure"

    def is_configured(self) -> bool:
        return True

    async def publish(self, client: httpx.AsyncClient, message: str) -> dict:
        raise RuntimeError("Simulated platform failure")


class FakeUnconfiguredPlatform(BasePlatform):
    name = "FakeUnconfigured"

    def is_configured(self) -> bool:
        return False

    async def publish(self, client: httpx.AsyncClient, message: str) -> dict:
        raise AssertionError("Should never be called when unconfigured")


# ---------------------------------------------------------------------------
# Input validation tests
# ---------------------------------------------------------------------------
def test_message_too_long_rejected():
    long_message = "a" * 190 + " https://example.com"
    response = client.post("/posting", json={"message": long_message})
    assert response.status_code == 422


def test_message_without_url_rejected():
    response = client.post("/posting", json={"message": "No link here at all"})
    assert response.status_code == 422


def test_message_with_two_urls_rejected():
    msg = "Check https://example.com and also https://another.com"
    response = client.post("/posting", json={"message": msg})
    assert response.status_code == 422


def test_message_with_invalid_url_rejected():
    response = client.post("/posting", json={"message": "Visit https://not a valid url"})
    assert response.status_code == 422


def test_valid_message_passes_validation():
    msg = "Check out our platform and grow your visibility. https://example.com"
    response = client.post("/posting", json={"message": msg})
    assert response.status_code == 200
    body = response.json()
    assert "success" in body
    assert "results" in body
    assert isinstance(body["results"], list)
    assert len(body["results"]) >= 1


# ---------------------------------------------------------------------------
# Posting orchestration tests (isolation + continue-on-failure behaviour)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_one_platform_failing_does_not_block_others():
    service = PostingService(
        platforms=[FakeSuccessPlatform(), FakeFailurePlatform(), FakeUnconfiguredPlatform()]
    )
    response = await service.publish_everywhere("Check this out https://example.com")

    assert response.success is True
    statuses = {r.platform: r.status for r in response.results}
    assert statuses["FakeSuccess"] == "success"
    assert statuses["FakeFailure"] == "failed"
    assert statuses["FakeUnconfigured"] == "failed"


@pytest.mark.asyncio
async def test_all_platforms_failing_reports_overall_failure():
    service = PostingService(platforms=[FakeFailurePlatform(), FakeUnconfiguredPlatform()])
    response = await service.publish_everywhere("Check this out https://example.com")

    assert response.success is False
    assert all(r.status == "failed" for r in response.results)


@pytest.mark.asyncio
async def test_success_result_contains_required_fields():
    service = PostingService(platforms=[FakeSuccessPlatform()])
    response = await service.publish_everywhere("Check this out https://example.com")

    result = response.results[0]
    assert result.status == "success"
    assert result.posted_url == "https://fake.example.com/post/1"
    assert result.public_access is True
    assert result.date is not None
    assert result.time is not None
    assert result.error is None
