from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.job import PipelineJob
from app.schemas.responses import ErrorResponse, JobResponse, ValidationErrorResponse

router = APIRouter()


@router.get(
    "/{job_id}",
    summary="Get pipeline job status",
    description="""
Returns the current state and all artefacts for a pipeline job.

### Polling guide

| Status | What to expect |
|---|---|
| `queued` | Job is waiting for a free Celery worker |
| `running` | Claude is generating the script — check back in ~10 seconds |
| `stitching` | All 4 Veo3 clips are ready; FFmpeg is concatenating |
| `publishing` | Video uploaded; posting to social channels |
| `completed` | `final_video_url` is populated with a 7-day signed URL |
| `failed` | `error_message` contains the failure reason |

Recommended poll interval: **15 seconds**. A typical job completes in **8–15 minutes**
(Veo3 clip generation is the bottleneck at ~1–3 min per clip).
""",
    response_model=JobResponse,
    responses={
        200: {
            "description": "Job found — returns current status and available artefacts.",
            "model": JobResponse,
        },
        404: {
            "description": "No job exists with the given ID.",
            "model": ErrorResponse,
        },
        422: {
            "description": "The `job_id` path parameter is not a valid UUID.",
            "model": ValidationErrorResponse,
        },
    },
)
async def get_job(job_id: UUID) -> JobResponse:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineJob).where(PipelineJob.id == job_id))
        job = result.scalar_one_or_none()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(
        job_id=job.id,
        status=job.status,
        lead_name=job.lead_name,
        lead_company=job.lead_company,
        script=job.script,
        clips=job.clips,
        final_video_url=job.final_video_url,
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )
