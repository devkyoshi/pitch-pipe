from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routers import jobs, webhook
from app.schemas.responses import HealthResponse

_DESCRIPTION = """
## Veo3 Lead Gen Video Pipeline API

Converts incoming sales leads into personalised 30-second marketing videos — fully automated.

### Pipeline flow

1. **Webhook** — `POST /webhook/lead` accepts a lead profile and enqueues a pipeline job.
2. **Script** — Claude (`claude-sonnet-4-6`) writes a 4-scene video script tailored to the lead.
3. **Clip generation** — Google Veo 3 (Vertex AI) renders one 8-second clip per scene.
4. **Stitching** — FFmpeg concatenates clips with a crossfade transition into a single MP4.
5. **Publishing** — The final video is posted to LinkedIn, Instagram Reels, and/or Meta Ads.
6. **Notification** — A Slack message is sent with the job summary and a link to the video.

### Job status lifecycle

```
queued → running → stitching → publishing → completed
                                          ↘ failed
```

Poll `GET /jobs/{job_id}` to track progress. The full stitched video URL is returned in
`final_video_url` once the job reaches `completed`.

### Authentication

All tokens are configured via environment variables — see `.env.example` for the full list.
This API itself does not enforce authentication; add a gateway/reverse-proxy layer for production.
"""

_TAGS = [
    {
        "name": "webhook",
        "description": (
            "Ingest a new lead and start the video generation pipeline. "
            "Returns a `job_id` immediately; the pipeline runs asynchronously."
        ),
    },
    {
        "name": "jobs",
        "description": (
            "Query the status and artefacts of a pipeline job. "
            "Poll this endpoint to track progress from `queued` through to `completed` or `failed`."
        ),
    },
    {
        "name": "system",
        "description": "Service health and readiness checks.",
    },
]

app = FastAPI(
    title="Veo3 Lead Gen Pipeline",
    version="1.0.0",
    description=_DESCRIPTION,
    openapi_tags=_TAGS,
    contact={
        "name": "Engineering Team",
        "email": "hgp.ashi@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])


@app.get(
    "/health",
    tags=["system"],
    summary="Health check",
    description="Returns `{\"status\": \"ok\"}` when the API process is running. Does not verify DB or Redis connectivity.",
    response_model=HealthResponse,
    responses={200: {"description": "Service is up"}},
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
