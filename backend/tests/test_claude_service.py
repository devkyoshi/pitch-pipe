import json
from unittest.mock import MagicMock, patch

import pytest

from app.models.lead import LeadPayload
from app.services.claude_service import ScriptGenerationError, generate_script

VALID_SCRIPT = {
    "video_title": "Transform Your SaaS Onboarding",
    "scenes": [
        {
            "order": 1,
            "narration": "Struggling with slow onboarding? You are not alone.",
            "veo_prompt": "Wide cinematic shot of a frustrated professional at a modern desk, cool blue lighting.",
            "duration_seconds": 8,
        },
        {
            "order": 2,
            "narration": "Our platform cuts onboarding time by 60 percent.",
            "veo_prompt": "Close-up of a laptop screen showing a sleek dashboard, warm golden lighting.",
            "duration_seconds": 8,
        },
        {
            "order": 3,
            "narration": "Teams at Acme Corp are already seeing results.",
            "veo_prompt": "Diverse team celebrating in a bright open office, natural sunlight, wide angle.",
            "duration_seconds": 8,
        },
        {
            "order": 4,
            "narration": "Start your free trial today.",
            "veo_prompt": "Clean product logo reveal on a white background, subtle lens flare.",
            "duration_seconds": 8,
        },
    ],
    "cta": "Start Free Trial",
}

LEAD = LeadPayload(
    name="Alice",
    company="Acme Corp",
    industry="SaaS",
    pain_point="slow onboarding",
    funnel_stage="awareness",
    target_channel=["linkedin"],
)


def _mock_gemini_response(text: str) -> MagicMock:
    response = MagicMock()
    response.text = text
    return response


@pytest.mark.anyio
async def test_generate_script_success():
    mock_model = MagicMock()
    mock_model.generate_content.return_value = _mock_gemini_response(json.dumps(VALID_SCRIPT))

    with patch("app.services.claude_service._get_model", return_value=mock_model):
        result = await generate_script(LEAD)

    assert result["video_title"] == VALID_SCRIPT["video_title"]
    assert len(result["scenes"]) == 4


@pytest.mark.anyio
async def test_generate_script_retries_on_bad_json():
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = [
        _mock_gemini_response("not valid json"),
        _mock_gemini_response("still not json"),
        _mock_gemini_response(json.dumps(VALID_SCRIPT)),
    ]

    with (
        patch("app.services.claude_service._get_model", return_value=mock_model),
        patch("app.services.claude_service.asyncio.sleep"),
    ):
        result = await generate_script(LEAD)

    assert result["video_title"] == VALID_SCRIPT["video_title"]
    assert mock_model.generate_content.call_count == 3


@pytest.mark.anyio
async def test_generate_script_raises_after_3_failures():
    mock_model = MagicMock()
    mock_model.generate_content.return_value = _mock_gemini_response("{{not json}}")

    with (
        patch("app.services.claude_service._get_model", return_value=mock_model),
        patch("app.services.claude_service.asyncio.sleep"),
    ):
        with pytest.raises(ScriptGenerationError):
            await generate_script(LEAD)

    assert mock_model.generate_content.call_count == 3


@pytest.mark.anyio
async def test_generate_script_strips_markdown_fences():
    fenced = f"```json\n{json.dumps(VALID_SCRIPT)}\n```"
    mock_model = MagicMock()
    mock_model.generate_content.return_value = _mock_gemini_response(fenced)

    with patch("app.services.claude_service._get_model", return_value=mock_model):
        result = await generate_script(LEAD)

    assert result["video_title"] == VALID_SCRIPT["video_title"]
