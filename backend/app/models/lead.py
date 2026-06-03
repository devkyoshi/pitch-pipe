from typing import List, Literal

from pydantic import BaseModel, Field


class LeadPayload(BaseModel):
    name: str = Field(..., description="Full name of the lead.", examples=["Jane Smith"])
    company: str = Field(..., description="Company or organisation the lead works for.", examples=["TechCorp"])
    industry: str = Field(
        ...,
        description="Industry vertical of the lead's company.",
        examples=["SaaS", "E-commerce", "Financial Services", "Healthcare"],
    )
    pain_point: str = Field(
        ...,
        description="The primary business problem the lead is trying to solve.",
        examples=["slow customer onboarding", "high cart abandonment rate"],
    )
    funnel_stage: Literal["awareness", "consideration", "decision"] = Field(
        ...,
        description=(
            "Lead's current position in the marketing funnel.\n\n"
            "- `awareness` — lead has just discovered the problem\n"
            "- `consideration` — lead is evaluating solutions\n"
            "- `decision` — lead is ready to buy"
        ),
        examples=["awareness"],
    )
    target_channel: List[Literal["linkedin", "instagram", "meta_ads"]] = Field(
        ...,
        description=(
            "One or more publishing destinations for the generated video.\n\n"
            "- `linkedin` — posted as a LinkedIn ugcPost\n"
            "- `instagram` — published as an Instagram Reel\n"
            "- `meta_ads` — uploaded to Meta Ads and attached to the configured campaign"
        ),
        examples=[["linkedin", "instagram"]],
        min_length=1,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Jane Smith",
                    "company": "TechCorp",
                    "industry": "SaaS",
                    "pain_point": "slow customer onboarding",
                    "funnel_stage": "awareness",
                    "target_channel": ["linkedin"],
                }
            ]
        }
    }
