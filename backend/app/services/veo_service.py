import asyncio
import time

import httpx
import google.auth.transport.requests
from google.oauth2 import service_account

from app.config import settings


class VeoError(Exception):
    pass


def _get_access_token() -> str:
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_APPLICATION_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token


async def submit_clip(scene_prompt: str, duration: int = 8) -> str:
    token = _get_access_token()
    region = settings.GOOGLE_REGION
    project = settings.GOOGLE_PROJECT_ID

    url = (
        f"https://{region}-aiplatform.googleapis.com/v1/projects/{project}"
        f"/locations/{region}/publishers/google/models/veo-3.0-generate-preview:predictLongRunning"
    )
    payload = {
        "instances": [
            {
                "prompt": scene_prompt,
                "parameters": {
                    "aspectRatio": "16:9",
                    "durationSeconds": duration,
                    "sampleCount": 1,
                    "enhancePrompt": True,
                },
            }
        ]
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

    operation_name = data.get("name")
    if not operation_name:
        raise VeoError(f"No operation name in Veo response: {data}")
    return operation_name


async def poll_until_done(operation_name: str, timeout: int = 600) -> str:
    token = _get_access_token()
    region = settings.GOOGLE_REGION
    url = f"https://{region}-aiplatform.googleapis.com/v1/{operation_name}"

    deadline = time.monotonic() + timeout

    async with httpx.AsyncClient(timeout=30) as client:
        while time.monotonic() < deadline:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("done"):
                try:
                    gcs_uri = data["response"]["videos"][0]["gcsUri"]
                    return gcs_uri
                except (KeyError, IndexError) as exc:
                    raise VeoError(f"Unexpected Veo response structure: {data}") from exc

            await asyncio.sleep(20)

            # Refresh token before it expires (poll loop can be long)
            token = _get_access_token()
            client.headers.update({"Authorization": f"Bearer {token}"})

    raise VeoError(f"Veo operation timed out after {timeout}s: {operation_name}")
