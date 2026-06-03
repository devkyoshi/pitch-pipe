"""Pydantic response schemas — used by routers for OpenAPI type annotations."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Job summary (list view)
# ---------------------------------------------------------------------------


class JobSummary(BaseModel):
    job_id:          UUID = Field(..., description="Unique job ID.")
    status:          str  = Field(..., description="Current pipeline status.")
    lead_name:       str  = Field(..., description="Name of the lead.")
    lead_company:    Optional[str] = Field(None)
    target_channels: List[str]     = Field(default_factory=list)
    final_video_url: Optional[str] = Field(None)
    error_message:   Optional[str] = Field(None)
    created_at:      Optional[datetime] = Field(None)
    completed_at:    Optional[datetime] = Field(None)


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------


class WebhookResponse(BaseModel):
    job_id: UUID = Field(..., description="Unique identifier for the created pipeline job.")
    status: Literal["queued"] = Field("queued", description="Initial job status after enqueue.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "queued",
                }
            ]
        }
    }


# ---------------------------------------------------------------------------
# Script / scenes
# ---------------------------------------------------------------------------


class SceneSchema(BaseModel):
    order: int = Field(..., description="Scene number (1–4).", ge=1, le=4)
    narration: str = Field(..., description="Voiceover text (max 25 words).")
    veo_prompt: str = Field(
        ...,
        description="Cinematic visual description sent to Veo 3 (40–60 words, includes lighting, mood, camera angle).",
    )
    duration_seconds: int = Field(..., description="Clip duration in seconds (7–8).", ge=7, le=8)


class ScriptSchema(BaseModel):
    video_title: str = Field(..., description="Generated title for the marketing video.")
    scenes: List[SceneSchema] = Field(..., description="Ordered list of 4 scenes.")
    cta: str = Field(..., description="Call-to-action text overlay shown at the end.")


# ---------------------------------------------------------------------------
# Job
# ---------------------------------------------------------------------------


class JobResponse(BaseModel):
    job_id: UUID = Field(..., description="Unique pipeline job ID.")
    status: Literal["queued", "running", "stitching", "publishing", "completed", "failed"] = Field(
        ...,
        description=(
            "Current pipeline status.\n\n"
            "| Status | Meaning |\n"
            "|---|---|\n"
            "| `queued` | Waiting for a Celery worker |\n"
            "| `running` | Claude is generating the script |\n"
            "| `stitching` | Veo3 clips ready; FFmpeg is stitching |\n"
            "| `publishing` | Uploading to social channels |\n"
            "| `completed` | All steps finished successfully |\n"
            "| `failed` | A step failed; see `error_message` |"
        ),
    )
    lead_name: str = Field(..., description="Name of the lead that triggered this job.")
    lead_company: Optional[str] = Field(None, description="Company of the lead.")
    script: Optional[ScriptSchema] = Field(
        None,
        description="Claude-generated 4-scene script. Populated after the `running` phase.",
    )
    clips: Optional[List[str]] = Field(
        None,
        description="GCS URIs of individual Veo3-generated clips (one per scene). Populated after the `stitching` phase.",
    )
    final_video_url: Optional[str] = Field(
        None,
        description="7-day signed GCS URL for the final stitched video. Populated after `stitching`.",
    )
    error_message: Optional[str] = Field(
        None,
        description="Human-readable error detail when `status` is `failed`.",
    )
    created_at: Optional[datetime] = Field(None, description="UTC timestamp when the job was created.")
    completed_at: Optional[datetime] = Field(
        None, description="UTC timestamp when the job reached `completed` or `failed`."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "completed",
                    "lead_name": "Jane Smith",
                    "lead_company": "TechCorp",
                    "script": {
                        "video_title": "Transform Your SaaS Onboarding",
                        "scenes": [
                            {
                                "order": 1,
                                "narration": "Struggling with slow onboarding? You are not alone.",
                                "veo_prompt": "Wide cinematic shot of a frustrated professional at a modern desk, cool blue lighting, shallow depth of field, eye-level camera angle.",
                                "duration_seconds": 8,
                            },
                            {
                                "order": 2,
                                "narration": "Our platform cuts onboarding time by 60 percent.",
                                "veo_prompt": "Close-up of a laptop screen showing a sleek SaaS dashboard with green metrics, warm golden hour lighting, rack focus from hands to screen.",
                                "duration_seconds": 8,
                            },
                            {
                                "order": 3,
                                "narration": "Teams at TechCorp are already seeing results.",
                                "veo_prompt": "Diverse team celebrating in a bright open-plan office, natural sunlight through floor-to-ceiling windows, wide angle tracking shot.",
                                "duration_seconds": 8,
                            },
                            {
                                "order": 4,
                                "narration": "Start your free trial today. No credit card required.",
                                "veo_prompt": "Clean product logo reveal on a white background, subtle lens flare, centered composition, slow zoom in.",
                                "duration_seconds": 8,
                            },
                        ],
                        "cta": "Start Free Trial",
                    },
                    "clips": [
                        "gs://my-bucket/550e8400/clip_1.mp4",
                        "gs://my-bucket/550e8400/clip_2.mp4",
                        "gs://my-bucket/550e8400/clip_3.mp4",
                        "gs://my-bucket/550e8400/clip_4.mp4",
                    ],
                    "final_video_url": "https://storage.googleapis.com/my-bucket/550e8400/final.mp4?X-Goog-Signature=...",
                    "error_message": None,
                    "created_at": "2026-06-03T10:00:00Z",
                    "completed_at": "2026-06-03T10:14:32Z",
                }
            ]
        }
    }


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable error description.")

    model_config = {
        "json_schema_extra": {
            "examples": [{"detail": "Job not found"}]
        }
    }


class ValidationErrorDetail(BaseModel):
    loc: List[Any] = Field(..., description="Location of the invalid field.")
    msg: str = Field(..., description="Validation error message.")
    type: str = Field(..., description="Error type identifier.")


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorDetail] = Field(..., description="List of validation errors.")


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: Literal["ok"] = Field("ok", description="Service health status.")
