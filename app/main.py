"""FastAPI application exposing the /posting endpoint."""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import JSONResponse

from app.schemas import PostRequest, PostResponse
from app.services.posting_service import posting_service

app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description=(
        "Publishes a short message with a single CTA link across multiple "
        "third-party platforms (Telegram, Discord, Slack, Mastodon, GitHub Gist)."
    ),
    version="1.0.0",
    redoc_url=None,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Return clean, human-readable validation error messages."""
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"] if loc != "body"),
                "message": error["msg"],
            }
        )
    return JSONResponse(status_code=422, content={"success": False, "errors": errors})


@app.get("/")
async def root():
    return {
        "service": "Automated Multi-Platform Posting System",
        "docs": "/docs",
        "endpoint": "POST /posting",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/redoc", include_in_schema=False)
async def redoc():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js",
    )


@app.post("/posting", response_model=PostResponse)
async def create_post(request: PostRequest):
    """
    Publish `message` across all configured third-party platforms.

    - Validates: max 200 chars, exactly one valid CTA URL.
    - Posts to each platform independently; one failure never blocks others.
    """
    return await posting_service.publish_everywhere(request.message)
