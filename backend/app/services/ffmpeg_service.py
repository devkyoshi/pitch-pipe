import asyncio
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import List

from google.cloud import storage
from google.oauth2 import service_account

from app.config import settings


def _gcs_client() -> storage.Client:
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_APPLICATION_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return storage.Client(project=settings.GOOGLE_PROJECT_ID, credentials=credentials)


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    """Return (bucket_name, blob_name) from a gs:// URI."""
    assert uri.startswith("gs://"), f"Expected gs:// URI, got {uri}"
    parts = uri[5:].split("/", 1)
    return parts[0], parts[1]


async def stitch_and_upload(job_id: str, clip_uris: List[str]) -> str:
    tmp_dir = Path(f"/tmp/{job_id}")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        client = _gcs_client()

        # Download clips from GCS
        local_clips: List[Path] = []
        for idx, uri in enumerate(clip_uris):
            bucket_name, blob_name = _parse_gcs_uri(uri)
            local_path = tmp_dir / f"clip_{idx + 1}.mp4"
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.download_to_filename(str(local_path))
            local_clips.append(local_path)

        # Write concat.txt
        concat_file = tmp_dir / "concat.txt"
        concat_file.write_text(
            "\n".join(f"file '{clip.name}'" for clip in local_clips)
        )

        # Run FFmpeg with xfade crossfade
        output_file = tmp_dir / f"final_{job_id}.mp4"
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-vf", "xfade=transition=fade:duration=0.3:offset=7.7",
            "-c:v", "libx264", "-crf", "23", "-preset", "fast",
            "-movflags", "+faststart",
            str(output_file),
        ]

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(ffmpeg_cmd, capture_output=True, cwd=str(tmp_dir)),
        )
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr.decode()}")

        # Upload final video to GCS
        dest_blob_name = f"{job_id}/final.mp4"
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        blob = bucket.blob(dest_blob_name)
        blob.upload_from_filename(str(output_file), content_type="video/mp4")

        # Generate 7-day signed URL
        signed_url = blob.generate_signed_url(
            expiration=timedelta(days=7),
            method="GET",
            version="v4",
            credentials=service_account.Credentials.from_service_account_file(
                settings.GOOGLE_APPLICATION_CREDENTIALS
            ),
        )
        return signed_url

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
