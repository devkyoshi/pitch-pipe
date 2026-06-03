import asyncio
import json

import anthropic

from app.config import settings
from app.models.lead import LeadPayload


class ScriptGenerationError(Exception):
    pass


_SYSTEM_PROMPT = "You are a marketing video scriptwriter."

_USER_PROMPT_TEMPLATE = """Given this lead profile:
- Name: {name}
- Company: {company}
- Industry: {industry}
- Pain point: {pain_point}
- Funnel stage: {funnel_stage}

Generate a 4-scene video script for a 30-second marketing ad.
Each scene must be exactly 7-8 seconds when read aloud.

Return ONLY a valid JSON object - no markdown, no preamble:
{{
  "video_title": "string",
  "scenes": [
    {{
      "order": 1,
      "narration": "string (voiceover text, max 25 words)",
      "veo_prompt": "string (visual scene description for Veo 3, cinematic, 40-60 words, include lighting, mood, camera angle)",
      "duration_seconds": 8
    }}
  ],
  "cta": "string (final call to action text overlay)"
}}"""


async def generate_script(lead: LeadPayload) -> dict:
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompt = _USER_PROMPT_TEMPLATE.format(
        name=lead.name,
        company=lead.company,
        industry=lead.industry,
        pain_point=lead.pain_point,
        funnel_stage=lead.funnel_stage,
    )

    last_error: Exception | None = None
    for attempt in range(3):
        if attempt > 0:
            await asyncio.sleep(2**attempt)
        try:
            response = await client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            script = json.loads(raw)
            if "scenes" not in script or "video_title" not in script:
                raise ScriptGenerationError("Missing required fields in script JSON")
            return script
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            last_error = ScriptGenerationError(f"Failed to parse script JSON: {exc}")
        except ScriptGenerationError as exc:
            last_error = exc

    raise last_error or ScriptGenerationError("Script generation failed after 3 attempts")
