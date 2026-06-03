from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.session import AsyncSessionLocal
from app.models.job import PipelineJob
from app.models.lead import LeadPayload
from app.schemas.responses import ErrorResponse, ValidationErrorResponse, WebhookResponse

router = APIRouter()


@router.post(
    "/lead",
    summary="Submit a new lead",
    description="""
Accepts a lead profile, persists a `PipelineJob` record (status: `queued`), and enqueues
the async Celery pipeline task.

**The response is immediate** — the video generation runs in the background.
Use `GET /jobs/{job_id}` to track progress.

### Pipeline triggered
1. Claude generates a 4-scene video script
2. Veo 3 renders one clip per scene (~1–3 min each)
3. FFmpeg stitches clips with crossfade into a final MP4
4. Video is published to each channel in `target_channel`
5. Slack notification sent on completion
""",
    response_model=WebhookResponse,
    status_code=200,
    responses={
        200: {
            "description": "Lead accepted — pipeline job created and enqueued.",
            "model": WebhookResponse,
        },
        422: {
            "description": "Request body validation failed.",
            "model": ValidationErrorResponse,
        },
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "awareness_linkedin": {
                            "summary": "Awareness stage — LinkedIn only",
                            "value": {
                                "name": "Jane Smith",
                                "company": "TechCorp",
                                "industry": "SaaS",
                                "pain_point": "slow customer onboarding",
                                "funnel_stage": "awareness",
                                "target_channel": ["linkedin"],
                            },
                        },
                        "decision_all_channels": {
                            "summary": "Decision stage — all channels",
                            "value": {
                                "name": "John Doe",
                                "company": "RetailCo",
                                "industry": "E-commerce",
                                "pain_point": "high cart abandonment rate",
                                "funnel_stage": "decision",
                                "target_channel": ["linkedin", "instagram", "meta_ads"],
                            },
                        },
                        "consideration_meta": {
                            "summary": "Consideration stage — Meta only",
                            "value": {
                                "name": "Alice Brown",
                                "company": "FinTech Ltd",
                                "industry": "Financial Services",
                                "pain_point": "manual compliance reporting",
                                "funnel_stage": "consideration",
                                "target_channel": ["instagram", "meta_ads"],
                            },
                        },
                    }
                }
            }
        }
    },
)
async def receive_lead(payload: LeadPayload) -> JSONResponse:
    async with AsyncSessionLocal() as db:
        job = PipelineJob(
            lead_name=payload.name,
            lead_company=payload.company,
            lead_industry=payload.industry or None,
            pain_point=payload.pain_point or None,
            funnel_stage=payload.funnel_stage,
            target_channels=payload.target_channel or [],
            # Pre-populate script when user provides manual prompts (skips Claude step)
            script=payload.manual_script.model_dump() if payload.manual_script else None,
            status="queued",
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

    from app.tasks.pipeline_task import run_pipeline

    run_pipeline.delay(str(job.id))

    return JSONResponse({"job_id": str(job.id), "status": "queued"}, status_code=200)
