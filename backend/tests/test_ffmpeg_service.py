import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from app.services.ffmpeg_service import stitch_and_upload


@pytest.mark.anyio
async def test_stitch_and_upload_writes_concat_and_calls_ffmpeg():
    job_id = str(uuid.uuid4())
    clip_uris = [
        f"gs://my-bucket/{job_id}/clip_1.mp4",
        f"gs://my-bucket/{job_id}/clip_2.mp4",
    ]

    mock_blob = MagicMock()
    mock_blob.download_to_filename = MagicMock()
    mock_blob.upload_from_filename = MagicMock()
    mock_blob.generate_signed_url = MagicMock(return_value="https://signed.url/video.mp4")

    mock_bucket = MagicMock()
    mock_bucket.blob = MagicMock(return_value=mock_blob)

    mock_gcs_client = MagicMock()
    mock_gcs_client.bucket = MagicMock(return_value=mock_bucket)

    mock_ffmpeg_result = MagicMock()
    mock_ffmpeg_result.returncode = 0
    mock_ffmpeg_result.stderr = b""

    with (
        patch("app.services.ffmpeg_service._gcs_client", return_value=mock_gcs_client),
        patch("app.services.ffmpeg_service.service_account.Credentials.from_service_account_file"),
        patch("app.services.ffmpeg_service.subprocess.run", return_value=mock_ffmpeg_result) as mock_subprocess,
        patch("app.services.ffmpeg_service.shutil.rmtree"),
    ):
        signed_url = await stitch_and_upload(job_id, clip_uris)

    # Assert ffmpeg was called
    mock_subprocess.assert_called_once()
    ffmpeg_args = mock_subprocess.call_args[0][0]
    assert ffmpeg_args[0] == "ffmpeg"
    assert "-f" in ffmpeg_args
    assert "concat" in ffmpeg_args

    # Assert concat.txt would have been written (via download side effect being set)
    assert mock_blob.download_to_filename.call_count == 2

    # Assert upload was called for the final video
    mock_blob.upload_from_filename.assert_called_once()

    # Assert signed URL is returned
    assert signed_url == "https://signed.url/video.mp4"


@pytest.mark.anyio
async def test_stitch_and_upload_raises_on_ffmpeg_failure():
    job_id = str(uuid.uuid4())
    clip_uris = [f"gs://my-bucket/{job_id}/clip_1.mp4"]

    mock_blob = MagicMock()
    mock_blob.download_to_filename = MagicMock()

    mock_bucket = MagicMock()
    mock_bucket.blob = MagicMock(return_value=mock_blob)

    mock_gcs_client = MagicMock()
    mock_gcs_client.bucket = MagicMock(return_value=mock_bucket)

    mock_ffmpeg_result = MagicMock()
    mock_ffmpeg_result.returncode = 1
    mock_ffmpeg_result.stderr = b"FFmpeg error: codec not found"

    with (
        patch("app.services.ffmpeg_service._gcs_client", return_value=mock_gcs_client),
        patch("app.services.ffmpeg_service.service_account.Credentials.from_service_account_file"),
        patch("app.services.ffmpeg_service.subprocess.run", return_value=mock_ffmpeg_result),
        patch("app.services.ffmpeg_service.shutil.rmtree"),
    ):
        with pytest.raises(RuntimeError, match="FFmpeg failed"):
            await stitch_and_upload(job_id, clip_uris)
