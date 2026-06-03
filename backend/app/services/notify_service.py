from typing import Dict

import httpx

from app.config import settings


async def notify_completion(
    job_id: str,
    lead_name: str,
    company: str,
    status: str,
    channels: Dict[str, str],
    signed_url: str,
) -> None:
    channel_summary = ", ".join(
        f"{ch} ({result})" for ch, result in channels.items()
    )

    emoji = "✅" if status == "completed" else "❌"
    payload = {
        "text": f"{emoji} Video pipeline {status}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Lead:* {lead_name} @ {company}\n"
                        f"*Job:* {job_id}\n"
                        f"*Status:* {status}"
                    ),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Published to:* {channel_summary}\n"
                        f"*Video:* <{signed_url}|Watch final video>"
                    ),
                },
            },
        ],
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(settings.SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
