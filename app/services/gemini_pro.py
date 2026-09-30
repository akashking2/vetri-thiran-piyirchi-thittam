import json
import re
from typing import List, Dict

from app.config import GEMINI_API_KEY, GEMINI_MODEL


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


def generate_story(outline: List[Dict], character_name: str, tone: str) -> List[Dict]:
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key is not configured.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
Expand this comic outline into panel-by-panel narration and dialogue.

Character: {character_name}
Tone: {tone}
Outline:
{json.dumps(outline, ensure_ascii=False)}

Return ONLY a JSON array with one object per panel.
Preserve panel_number, title, scene_description and image_prompt.
Add:
caption, narration, dialogue

Keep dialogue short and natural. Keep the story family-friendly.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.85,
            response_mime_type="application/json",
        ),
    )
    data = _extract_json(response.text or "")
    if not isinstance(data, list):
        raise ValueError("Gemini returned invalid story data.")
    return data
