import json
import re
from typing import List, Dict

from app.config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TIMEOUT


def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.I).strip()
        text = re.sub(r"```$", "", text).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("Gemini did not return a JSON array.")
    return json.loads(text[start:end + 1])


def generate_outline(story_prompt: str, character_name: str, setting: str,
                     tone: str, art_style: str, panels: int = 5) -> List[Dict]:
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key is not configured.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
Create a coherent {panels}-panel comic outline.

Story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY a JSON array. No markdown and no explanation.
Each array item must contain exactly:
panel_number, title, scene_description, image_prompt

The image_prompt must describe the visual scene and must not request text,
speech bubbles, captions, logos, signatures, or watermarks.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
        ),
    )

    data = _extract_json(response.text or "")
    if not isinstance(data, list) or len(data) < 3:
        raise ValueError("Gemini returned an invalid outline.")

    return data[:panels]
