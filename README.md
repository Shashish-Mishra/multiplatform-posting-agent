# Automated Multi-Platform Posting System

A FastAPI service that validates a short message (≤200 chars, containing
exactly one CTA link) and automatically publishes it to **5 independent
third-party platforms** using their official REST APIs:

| # | Platform | API used | Docs |
|---|----------|----------|------|
| 1 | **Telegram** | Bot API – `sendMessage` | https://core.telegram.org/bots/api#sendmessage |
| 2 | **Discord**  | Incoming Webhook – `execute webhook` | https://discord.com/developers/docs/resources/webhook#execute-webhook |
| 3 | **Slack**    | Incoming Webhook | https://api.slack.com/messaging/webhooks |
| 4 | **Mastodon** | REST API – `POST /api/v1/statuses` | https://docs.joinmastodon.org/methods/statuses/#create |
| 5 | **GitHub Gist** | REST API – `POST /gists` | https://docs.github.com/en/rest/gists/gists#create-a-gist |

Each platform integration is handled **independently**: if one platform
fails (missing credentials, auth error, network error, rate limit, etc.)
the remaining platforms are still attempted and the overall request still
succeeds as long as at least one platform publishes successfully.

---

## 1. Project Structure

```text
automated-posting/
├── app/
│   ├── main.py                       # FastAPI app + /posting endpoint
│   ├── schemas.py                    # Pydantic request/response models + validation
│   ├── config.py                     # Settings loaded from environment variables
│   ├── platforms/
│   │   ├── base.py                   # Abstract base class (template method pattern)
│   │   ├── telegram_platform.py
│   │   ├── discord_platform.py
│   │   ├── slack_platform.py
│   │   ├── mastodon_platform.py
│   │   └── github_gist_platform.py
│   └── services/
│       └── posting_service.py        # Fans out to all platforms concurrently
├── tests/
│   └── test_posting.py               # Validation + orchestration tests
├── .env.example
├── requirements.txt
└── README.md
```

---

## 2. Setup & Execution

### Prerequisites
- Python 3.10+

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure credentials (optional)

```bash
cp .env.example .env
# edit .env and fill in whichever platforms you have credentials for
```

> The service works even with **zero** credentials configured — each
> platform simply reports `status: "failed"` with
> `"error": "Platform not configured (missing credentials)."` instead of
> crashing the app. This lets you review the API contract/behavior without
> needing all 5 accounts set up.

### Run the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

### Interactive API docs

Open: http://localhost:4000/docs (Swagger UI) or http://localhost:4000/redoc

### Run tests

```bash
pytest tests/ -v
```

---

## 3. How to obtain credentials for each platform

| Platform | Steps |
|---|---|
| **Telegram** | Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token into `TELEGRAM_BOT_TOKEN`. Add the bot to a channel/group, send any message, then call `https://api.telegram.org/bot<token>/getUpdates` to find the `chat.id` → set `TELEGRAM_CHAT_ID`. |
| **Discord** | Server → Channel Settings → Integrations → Webhooks → **New Webhook** → copy URL into `DISCORD_WEBHOOK_URL`. |
| **Slack** | Create a Slack App at https://api.slack.com/apps → enable **Incoming Webhooks** → **Add New Webhook to Workspace** → copy URL into `SLACK_WEBHOOK_URL`. |
| **Mastodon** | On your instance (e.g. mastodon.social) → Preferences → Development → **New Application** → grant `write:statuses` scope → copy access token into `MASTODON_ACCESS_TOKEN`, set `MASTODON_INSTANCE_URL`. |
| **GitHub Gist** | https://github.com/settings/tokens → **Generate new token (classic)** → scope `gist` → copy into `GITHUB_TOKEN`. |

No API keys, passwords, or tokens are committed to this repository — only
placeholder names in `.env.example`.

---

## 4. API Reference

### `POST /posting`

**Request body**

```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

**Validation rules**
- `message` must not exceed **200 characters**.
- `message` must contain **exactly one** CTA link (URL).
- The URL must be a syntactically valid `http(s)://` URL.
- Platform selection is handled **internally** — the caller does not choose platforms.

**Validation error response (HTTP 422)**

```json
{
  "success": false,
  "errors": [
    {
      "field": "message",
      "message": "Value error, Message must contain exactly one CTA link (none found)."
    }
  ]
}
```

**Success response (HTTP 200)**

```json
{
  "success": false,
  "results": [
    {
      "platform": "Telegram",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Platform not configured (missing credentials)."
    },
    {
      "platform": "Discord",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Platform not configured (missing credentials)."
    },
    {
      "platform": "Slack",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Platform not configured (missing credentials)."
    },
    {
      "platform": "Mastodon",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Platform not configured (missing credentials)."
    },
    {
      "platform": "GitHub Gist",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Platform not configured (missing credentials)."
    }
  ]
}
```

With valid Telegram + GitHub Gist credentials configured, a response would
look like:

```json
{
  "success": true,
  "results": [
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/my_public_channel/42",
      "public_access": true,
      "date": "2026-11-17",
      "time": "10:30:00",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Platform not configured (missing credentials)."
    },
    {
      "platform": "Slack",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Platform not configured (missing credentials)."
    },
    {
      "platform": "Mastodon",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Platform not configured (missing credentials)."
    },
    {
      "platform": "GitHub Gist",
      "status": "success",
      "posted_url": "https://gist.github.com/yourname/abc123def456",
      "public_access": true,
      "date": "2026-11-17",
      "time": "10:30:01",
      "error": null
    }
  ]
}
```

---

## 5. Sample requests (curl)

**Valid request:**

```bash
curl -s -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message":"Check out our latest business platform and grow your online visibility. https://example.com"}'
```

**Message too long (>200 chars) → 422:**

```bash
curl -s -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message":"'"$(python3 -c "print('a'*190 + ' https://example.com')")"'"}'
```

**Missing CTA link → 422:**

```bash
curl -s -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message":"No link here at all"}'
```

**Two CTA links → 422:**

```bash
curl -s -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message":"Check https://example.com and https://another.com"}'
```

---

## 6. Design notes

- **`BasePlatform`** (`app/platforms/base.py`) implements the *template
  method* pattern: subclasses only implement `is_configured()` and
  `publish()`; the base class handles timing, success/failure wrapping,
  and exception isolation so one bad integration can never break the
  endpoint or affect other platforms.
- **`PostingService`** (`app/services/posting_service.py`) fans the
  message out to all registered platforms concurrently using
  `asyncio.gather`, so slow platforms don't serialize the whole request.
- Adding a 6th platform only requires: (1) a new class in
  `app/platforms/` implementing `BasePlatform`, and (2) registering it in
  `PLATFORMS` inside `posting_service.py`.
- Credentials are read via `pydantic-settings` from environment variables
  / `.env` — nothing is hardcoded, nothing sensitive is committed.

---

## 7. Running tests

```bash
pytest tests/ -v
```

Tests cover:
- Message length validation (>200 chars rejected).
- Exactly-one-CTA-link validation (0 or 2+ links rejected).
- URL format validation.
- Valid message passes and returns a well-formed response.
- Multi-platform orchestration: one platform failing does not block the
  others (`asyncio.gather` + per-platform exception isolation), using
  fake platform doubles so the test suite doesn't depend on network
  access or real credentials.
