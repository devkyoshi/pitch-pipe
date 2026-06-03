"""
Script generation via Google Gemini (google-genai SDK).
Kept as claude_service.py so existing imports don't change.
"""
import asyncio
import json

from google import genai
from google.genai import types

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


def _get_client() -> genai.Client:
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _call_gemini(prompt: str) -> str:
    """Synchronous Gemini call — run in executor to stay non-blocking."""
    client = _get_client()
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            temperature=0.7,
            max_output_tokens=1024,
        ),
    )
    return response.text.strip()


def _clean_json(raw: str) -> str:
    """Strip markdown code fences Gemini sometimes adds."""
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


async def generate_script(lead: LeadPayload) -> dict:
    prompt = _USER_PROMPT_TEMPLATE.format(
        name=lead.name,
        company=lead.company,
        industry=lead.industry,
        pain_point=lead.pain_point,
        funnel_stage=lead.funnel_stage,
    )

    loop = asyncio.get_event_loop()
    last_error: Exception | None = None

    for attempt in range(3):
        if attempt > 0:
            await asyncio.sleep(2 ** attempt)
        try:
            raw = await loop.run_in_executor(None, _call_gemini, prompt)
            script = json.loads(_clean_json(raw))
            if "scenes" not in script or "video_title" not in script:
                raise ScriptGenerationError("Missing required fields in script JSON")
            return script
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            last_error = ScriptGenerationError(f"Failed to parse script JSON: {exc}")
        except ScriptGenerationError as exc:
            last_error = exc

    raise last_error or ScriptGenerationError("Script generation failed after 3 attempts")
