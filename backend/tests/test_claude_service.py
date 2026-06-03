import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.lead import LeadPayload
from app.services.claude_service import ScriptGenerationError, generate_script

VALID_SCRIPT = {
    "video_title": "Transform Your SaaS Onboarding",
    "scenes": [
        {
            "order": 1,
            "narration": "Struggling with slow onboarding? You are not alone.",
            "veo_prompt": "Wide cinematic shot of a frustrated professional at a modern desk, cool blue lighting, shallow depth of field.",
            "duration_seconds": 8,
        },
        {
            "order": 2,
            "narration": "Our platform cuts onboarding time by 60 percent.",
            "veo_prompt": "Close-up of a laptop screen showing a sleek dashboard, warm golden lighting, rack focus.",
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
            "veo_prompt": "Clean product logo reveal on a white background, subtle lens flare, centered composition.",
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


def _make_mock_response(text: str) -> MagicMock:
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


@pytest.mark.anyio
async def test_generate_script_success():
    mock_create = AsyncMock(return_value=_make_mock_response(json.dumps(VALID_SCRIPT)))

    with patch("app.services.claude_service.anthropic.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create = mock_create
        mock_cls.return_value = mock_client

        result = await generate_script(LEAD)

    assert result["video_title"] == VALID_SCRIPT["video_title"]
    assert len(result["scenes"]) == 4
    mock_create.assert_called_once()


@pytest.mark.anyio
async def test_generate_script_retries_on_bad_json():
    bad_response = _make_mock_response("not valid json at all")
    good_response = _make_mock_response(json.dumps(VALID_SCRIPT))

    mock_create = AsyncMock(side_effect=[bad_response, bad_response, good_response])

    with patch("app.services.claude_service.anthropic.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create = mock_create
        mock_cls.return_value = mock_client

        with patch("app.services.claude_service.asyncio.sleep", AsyncMock()):
            result = await generate_script(LEAD)

    assert result["video_title"] == VALID_SCRIPT["video_title"]
    assert mock_create.call_count == 3


@pytest.mark.anyio
async def test_generate_script_raises_after_3_failures():
    bad_response = _make_mock_response("{{not json}}")
    mock_create = AsyncMock(return_value=bad_response)

    with patch("app.services.claude_service.anthropic.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create = mock_create
        mock_cls.return_value = mock_client

        with patch("app.services.claude_service.asyncio.sleep", AsyncMock()):
            with pytest.raises(ScriptGenerationError):
                await generate_script(LEAD)

    assert mock_create.call_count == 3
