import asyncio
from typing import Dict, List

import httpx

from app.config import settings


class PublishError(Exception):
    def __init__(self, channel: str, detail: str) -> None:
        self.channel = channel
        self.detail = detail
        super().__init__(f"[{channel}] {detail}")


async def publish_linkedin(signed_url: str, title: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        # Step 1: Register upload
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                "owner": settings.LINKEDIN_AUTHOR_URN,
                "serviceRelationships": [
                    {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
                ],
            }
        }
        reg_response = await client.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            json=register_payload,
            headers=headers,
        )
        if reg_response.status_code not in (200, 201):
            raise PublishError("linkedin", f"Register upload failed: {reg_response.text}")

        reg_data = reg_response.json()
        upload_url = reg_data["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset = reg_data["value"]["asset"]

        # Step 2: Upload video binary from signed URL
        video_resp = await client.get(signed_url)
        if video_resp.status_code != 200:
            raise PublishError("linkedin", "Failed to fetch video from signed URL")

        upload_resp = await client.put(
            upload_url,
            content=video_resp.content,
            headers={"Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}"},
        )
        if upload_resp.status_code not in (200, 201):
            raise PublishError("linkedin", f"Video upload failed: {upload_resp.text}")

        # Step 3: Create ugcPost
        post_payload = {
            "author": settings.LINKEDIN_AUTHOR_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": title},
                    "shareMediaCategory": "VIDEO",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": title},
                            "media": asset,
                            "title": {"text": title},
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        post_resp = await client.post(
            "https://api.linkedin.com/v2/ugcPosts",
            json=post_payload,
            headers=headers,
        )
        if post_resp.status_code not in (200, 201):
            raise PublishError("linkedin", f"UGC post creation failed: {post_resp.text}")

    return post_resp.headers.get("x-restli-id", "ok")


async def publish_instagram(signed_url: str) -> str:
    base_url = "https://graph.facebook.com/v19.0"
    params_base = {"access_token": settings.META_ACCESS_TOKEN}

    async with httpx.AsyncClient(timeout=120) as client:
        # Step 1: Create container
        container_resp = await client.post(
            f"{base_url}/{settings.META_IG_USER_ID}/media",
            params={
                **params_base,
                "media_type": "REELS",
                "video_url": signed_url,
                "share_to_feed": "true",
            },
        )
        if container_resp.status_code != 200:
            raise PublishError("instagram", f"Container creation failed: {container_resp.text}")

        container_id = container_resp.json().get("id")
        if not container_id:
            raise PublishError("instagram", "No container ID in response")

        # Step 2: Poll container status
        for _ in range(30):
            await asyncio.sleep(10)
            status_resp = await client.get(
                f"{base_url}/{container_id}",
                params={**params_base, "fields": "status_code"},
            )
            status_code = status_resp.json().get("status_code")
            if status_code == "FINISHED":
                break
            if status_code == "ERROR":
                raise PublishError("instagram", f"Container processing error: {status_resp.text}")
        else:
            raise PublishError("instagram", "Container did not reach FINISHED state in time")

        # Step 3: Publish
        publish_resp = await client.post(
            f"{base_url}/{settings.META_IG_USER_ID}/media_publish",
            params={**params_base, "creation_id": container_id},
        )
        if publish_resp.status_code != 200:
            raise PublishError("instagram", f"Publish failed: {publish_resp.text}")

    return publish_resp.json().get("id", "ok")


async def publish_meta_ads(signed_url: str, title: str) -> str:
    base_url = "https://graph.facebook.com/v19.0"
    access_token = settings.META_ACCESS_TOKEN

    async with httpx.AsyncClient(timeout=120) as client:
        # Step 1: Upload video
        upload_resp = await client.post(
            f"{base_url}/{settings.META_AD_ACCOUNT_ID}/advideos",
            data={
                "access_token": access_token,
                "file_url": signed_url,
                "title": title,
            },
        )
        if upload_resp.status_code != 200:
            raise PublishError("meta_ads", f"Video upload failed: {upload_resp.text}")

        video_id = upload_resp.json().get("id")
        if not video_id:
            raise PublishError("meta_ads", "No video ID in upload response")

        # Step 2: Create ad creative
        creative_resp = await client.post(
            f"{base_url}/{settings.META_AD_ACCOUNT_ID}/adcreatives",
            data={
                "access_token": access_token,
                "name": f"Creative - {title}",
                "object_story_spec": str(
                    {
                        "video_data": {
                            "video_id": video_id,
                            "message": title,
                            "call_to_action": {"type": "LEARN_MORE"},
                        }
                    }
                ),
            },
        )
        if creative_resp.status_code != 200:
            raise PublishError("meta_ads", f"Creative creation failed: {creative_resp.text}")

        creative_id = creative_resp.json().get("id")
        if not creative_id:
            raise PublishError("meta_ads", "No creative ID in response")

        # Step 3: Create ad and attach to adset
        ad_resp = await client.post(
            f"{base_url}/{settings.META_AD_ACCOUNT_ID}/ads",
            data={
                "access_token": access_token,
                "name": f"Ad - {title}",
                "adset_id": settings.META_ADSET_ID,
                "creative": f'{{"creative_id":"{creative_id}"}}',
                "status": "PAUSED",
            },
        )
        if ad_resp.status_code != 200:
            raise PublishError("meta_ads", f"Ad creation failed: {ad_resp.text}")

    return ad_resp.json().get("id", "ok")


async def publish_all(channels: List[str], signed_url: str, title: str) -> Dict[str, str]:
    results: Dict[str, str] = {}

    handlers = {
        "linkedin": lambda: publish_linkedin(signed_url, title),
        "instagram": lambda: publish_instagram(signed_url),
        "meta_ads": lambda: publish_meta_ads(signed_url, title),
    }

    for channel in channels:
        handler = handlers.get(channel)
        if handler is None:
            results[channel] = "skipped: unknown channel"
            continue
        try:
            await handler()
            results[channel] = "ok"
        except PublishError as exc:
            results[channel] = f"failed: {exc.detail}"
        except Exception as exc:
            results[channel] = f"failed: {exc}"

    return results
