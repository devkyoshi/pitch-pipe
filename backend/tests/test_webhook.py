import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.job import PipelineJob


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _make_mock_job() -> PipelineJob:
    job = MagicMock(spec=PipelineJob)
    job.id = uuid.uuid4()
    job.status = "queued"
    return job


@pytest.mark.anyio
async def test_webhook_valid_payload_returns_job_id():
    mock_job = _make_mock_job()
    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_job.id) or None)

    with (
        patch("app.routers.webhook.AsyncSessionLocal", return_value=mock_session),
        patch("app.routers.webhook.run_pipeline") as mock_task,
    ):
        mock_task.delay = MagicMock()

        # Patch PipelineJob constructor to return our mock
        with patch("app.routers.webhook.PipelineJob", return_value=mock_job):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/webhook/lead",
                    json={
                        "name": "Alice",
                        "company": "Acme Corp",
                        "industry": "SaaS",
                        "pain_point": "slow onboarding",
                        "funnel_stage": "awareness",
                        "target_channel": ["linkedin"],
                    },
                )

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"


@pytest.mark.anyio
async def test_webhook_missing_field_returns_422():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/webhook/lead",
            json={
                "name": "Alice",
                # missing company, industry, pain_point, funnel_stage, target_channel
            },
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_webhook_invalid_funnel_stage_returns_422():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/webhook/lead",
            json={
                "name": "Alice",
                "company": "Acme",
                "industry": "SaaS",
                "pain_point": "slow onboarding",
                "funnel_stage": "unknown_stage",
                "target_channel": ["linkedin"],
            },
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_webhook_invalid_channel_returns_422():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/webhook/lead",
            json={
                "name": "Alice",
                "company": "Acme",
                "industry": "SaaS",
                "pain_point": "slow onboarding",
                "funnel_stage": "decision",
                "target_channel": ["tiktok"],
            },
        )
    assert response.status_code == 422
