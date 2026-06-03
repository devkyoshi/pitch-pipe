from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, desc

from app.db.session import AsyncSessionLocal
from app.models.job import PipelineJob
from app.schemas.responses import ErrorResponse, JobResponse, JobSummary, ValidationErrorResponse, WebhookResponse

router = APIRouter()

_RETRYABLE = {"failed", "completed"}


@router.get(
    "",
    summary="List pipeline jobs",
    description="Returns all pipeline jobs ordered by most recent first. Filter by status or paginate with `limit`/`offset`.",
    response_model=List[JobSummary],
)
async def list_jobs(
    status: Optional[str] = Query(default=None, description="Filter by status (queued, running, stitching, publishing, completed, failed)"),
    limit:  int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[JobSummary]:
    async with AsyncSessionLocal() as db:
        q = select(PipelineJob).order_by(desc(PipelineJob.created_at)).limit(limit).offset(offset)
        if status:
            q = q.where(PipelineJob.status == status)
        result = await db.execute(q)
        jobs = result.scalars().all()

    return [
        JobSummary(
            job_id=j.id,
            status=j.status,
            lead_name=j.lead_name,
            lead_company=j.lead_company,
            target_channels=j.target_channels or [],
            final_video_url=j.final_video_url,
            error_message=j.error_message,
            created_at=j.created_at,
            completed_at=j.completed_at,
        )
        for j in jobs
    ]


@router.get(
    "/{job_id}",
    summary="Get pipeline job status",
    description="""
Returns the current state and all artefacts for a pipeline job.

### Polling guide

| Status | What to expect |
|---|---|
| `queued` | Job is waiting for a free Celery worker |
| `running` | Gemini is generating the script |
| `stitching` | All 4 Veo3 clips are ready; FFmpeg is concatenating |
| `publishing` | Video uploaded; posting to social channels |
| `completed` | `final_video_url` is populated with a 7-day signed URL |
| `failed` | `error_message` contains the failure reason |

Recommended poll interval: **15 seconds**.
""",
    response_model=JobResponse,
    responses={
        200: {"description": "Job found.", "model": JobResponse},
        404: {"description": "No job with this ID.", "model": ErrorResponse},
        422: {"description": "Invalid UUID.", "model": ValidationErrorResponse},
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


@router.post(
    "/{job_id}/retry",
    summary="Retry a pipeline job",
    description="""
Resets a `failed` or `completed` job and re-enqueues it.

**Smart retry:** if the script was already generated before the failure, it is preserved and
Gemini is skipped on the next run — the pipeline resumes from the Veo3 clip step.
""",
    response_model=WebhookResponse,
    responses={
        200: {"description": "Job reset and re-queued."},
        400: {"description": "Job is not in a retryable state.", "model": ErrorResponse},
        404: {"description": "No job with this ID.", "model": ErrorResponse},
    },
)
async def retry_job(job_id: UUID) -> WebhookResponse:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineJob).where(PipelineJob.id == job_id))
        job = result.scalar_one_or_none()

        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status not in _RETRYABLE:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot retry a job with status '{job.status}'. Only failed or completed jobs can be retried.",
            )

        # Reset execution state — preserve script so Gemini is skipped if it already ran
        job.status        = "queued"
        job.error_message = None
        job.completed_at  = None
        job.clips         = None
        job.final_video_url = None
        await db.commit()

    from app.tasks.pipeline_task import run_pipeline
    run_pipeline.delay(str(job_id))

    return WebhookResponse(job_id=job_id, status="queued")
