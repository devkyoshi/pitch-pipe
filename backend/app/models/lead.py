from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class ManualScene(BaseModel):
    order:            int = Field(..., ge=1, le=4)
    narration:        str = Field(default="")
    veo_prompt:       str = Field(..., min_length=10)
    duration_seconds: int = Field(default=8, ge=1, le=30)


class ManualScript(BaseModel):
    video_title: str = Field(default="Custom Video")
    scenes:      List[ManualScene] = Field(..., min_length=1, max_length=4)
    cta:         str = Field(default="")


class LeadPayload(BaseModel):
    name:    str
    company: str

    # Claude-only fields — required when use_claude=True
    industry:    str = Field(default="")
    pain_point:  str = Field(default="")
    funnel_stage: Literal["awareness", "consideration", "decision"] = Field(default="awareness")

    # Script step
    use_claude:    bool                  = Field(default=True)
    manual_script: Optional[ManualScript] = Field(default=None)

    # Publish step — empty list = skip publishing
    target_channel: List[Literal["linkedin", "instagram", "meta_ads"]] = Field(default=[])

    @model_validator(mode="after")
    def validate_pipeline_config(self) -> "LeadPayload":
        if self.use_claude:
            if not self.industry or not self.pain_point:
                raise ValueError("industry and pain_point are required when use_claude is True")
        else:
            if not self.manual_script:
                raise ValueError("manual_script is required when use_claude is False")
        return self
