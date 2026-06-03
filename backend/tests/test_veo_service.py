from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.veo_service import VeoError, poll_until_done, submit_clip


def _make_httpx_response(data: dict, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = data
    response.raise_for_status = MagicMock()
    return response


@pytest.mark.anyio
async def test_submit_clip_returns_operation_name():
    mock_response = _make_httpx_response({"name": "projects/test/locations/us-central1/operations/op-123"})

    with (
        patch("app.services.veo_service._get_access_token", return_value="fake-token"),
        patch("app.services.veo_service.httpx.AsyncClient") as mock_client_cls,
    ):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        operation_name = await submit_clip("A cinematic scene of a busy office.", 8)

    assert operation_name == "projects/test/locations/us-central1/operations/op-123"


@pytest.mark.anyio
async def test_poll_until_done_handles_not_done_then_done():
    not_done_response = _make_httpx_response({"done": False})
    done_response = _make_httpx_response(
        {
            "done": True,
            "response": {"videos": [{"gcsUri": "gs://my-bucket/clips/op-123.mp4"}]},
        }
    )

    with (
        patch("app.services.veo_service._get_access_token", return_value="fake-token"),
        patch("app.services.veo_service.asyncio.sleep", AsyncMock()),
        patch("app.services.veo_service.httpx.AsyncClient") as mock_client_cls,
    ):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=[not_done_response, done_response])
        mock_client.headers = MagicMock()
        mock_client.headers.update = MagicMock()
        mock_client_cls.return_value = mock_client

        gcs_uri = await poll_until_done("projects/test/locations/us-central1/operations/op-123", timeout=600)

    assert gcs_uri == "gs://my-bucket/clips/op-123.mp4"
    assert mock_client.get.call_count == 2


@pytest.mark.anyio
async def test_poll_until_done_raises_on_timeout():
    with (
        patch("app.services.veo_service._get_access_token", return_value="fake-token"),
        patch("app.services.veo_service.asyncio.sleep", AsyncMock()),
        patch("app.services.veo_service.time.monotonic", side_effect=[0, 700]),
        patch("app.services.veo_service.httpx.AsyncClient") as mock_client_cls,
    ):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_make_httpx_response({"done": False}))
        mock_client.headers = MagicMock()
        mock_client.headers.update = MagicMock()
        mock_client_cls.return_value = mock_client

        with pytest.raises(VeoError, match="timed out"):
            await poll_until_done("op-name", timeout=600)
