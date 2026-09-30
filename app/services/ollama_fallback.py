"""
Optional local LLM fallback through Ollama.

If Ollama is not installed/running, callers simply fall back to local_story.py.
"""
import json
from typing import List, Dict
import httpx

from app.config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT


def _call(prompt: str) -> str:
    response = httpx.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get("response", "")


def generate_outline_ollama(story_prompt, character_name, setting, tone, art_style, panels=5):
    prompt = f"""
Return ONLY valid JSON array with {panels} comic panels.
Keys: panel_number,title,scene_description,image_prompt.
Story: {story_prompt}
Character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}
"""
    raw = _call(prompt)
    start, end = raw.find("["), raw.rfind("]")
    if start < 0 or end < 0:
        raise ValueError("Ollama did not return JSON.")
    data = json.loads(raw[start:end+1])
    return data[:panels]


def generate_story_ollama(outline: List[Dict], character_name: str, tone: str):
    prompt = f"""
Return ONLY valid JSON array. Expand each panel with caption, narration and dialogue.
Character: {character_name}
Tone: {tone}
Outline: {json.dumps(outline)}
"""
    raw = _call(prompt)
    start, end = raw.find("["), raw.rfind("]")
    if start < 0 or end < 0:
        raise ValueError("Ollama did not return JSON.")
    return json.loads(raw[start:end+1])
