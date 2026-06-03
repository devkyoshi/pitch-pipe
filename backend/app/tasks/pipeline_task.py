import asyncio
from datetime import datetime, timezone
from typing import List

from celery import Celery
from sqlalchemy import select

from app.config import settings

app_celery = Celery(
    "pipeline",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
app_celery.conf.update(
    task_soft_time_limit=900,
    task_time_limit=960,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


@app_celery.task(name="run_pipeline", bind=True, max_retries=0)
def run_pipeline(self, job_id: str) -> None:  # noqa: ARG001
    asyncio.run(_run_pipeline_async(job_id))


async def _run_pipeline_async(job_id: str) -> None:
    from app.db.session import AsyncSessionLocal
    from app.models.job import PipelineJob
    from app.services.claude_service import generate_script
    from app.services.ffmpeg_service import stitch_and_upload
    from app.services.notify_service import notify_completion
    from app.services.publish_service import publish_all
    from app.services.veo_service import poll_until_done, submit_clip

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineJob).where(PipelineJob.id == job_id))
        job = result.scalar_one_or_none()
        if job is None:
            raise ValueError(f"PipelineJob {job_id} not found")

        job.status = "running"
        await db.commit()

        lead_name      = job.lead_name
        lead_company   = job.lead_company or ""
        target_channels: List[str] = job.target_channels or []

        try:
            # ── Step 1: Script ──────────────────────────────────────────────
            # job.script is pre-populated when the user provided manual prompts.
            # If it is None, Claude generates it.
            if job.script is None:
                from app.models.lead import LeadPayload

                lead_payload = LeadPayload(
                    name=job.lead_name,
                    company=job.lead_company or "",
                    industry=job.lead_industry or "",
                    pain_point=job.pain_point or "",
                    funnel_stage=job.funnel_stage or "awareness",  # type: ignore[arg-type]
                    target_channel=target_channels,  # type: ignore[arg-type]
                )
                script = await generate_script(lead_payload)
                job.script = script
                await db.commit()
            else:
                script = job.script

            # ── Step 2 + 3: Clips → Stitch ─────────────────────────────────
            clip_uris: List[str] = []
            for scene in script.get("scenes", []):
                operation_name = await submit_clip(
                    scene["veo_prompt"], scene.get("duration_seconds", 8)
                )
                gcs_uri = await poll_until_done(operation_name, timeout=600)
                clip_uris.append(gcs_uri)

            job.clips = clip_uris
            job.status = "stitching"
            await db.commit()

            signed_url = await stitch_and_upload(str(job.id), clip_uris)
            job.final_video_url = signed_url
            await db.commit()

            # ── Step 4: Publish (optional) ──────────────────────────────────
            publish_results: dict = {}
            if target_channels:
                job.status = "publishing"
                await db.commit()

                publish_results = await publish_all(
                    target_channels,
                    signed_url,
                    script.get("video_title", "Marketing Video"),
                )

                await notify_completion(
                    job_id=str(job.id),
                    lead_name=lead_name,
                    company=lead_company,
                    status="completed",
                    channels=publish_results,
                    signed_url=signed_url,
                )

            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()

        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()

            try:
                await notify_completion(
                    job_id=str(job.id),
                    lead_name=lead_name,
                    company=lead_company,
                    status="failed",
                    channels={},
                    signed_url="",
                )
            except Exception:
                pass

            raise
