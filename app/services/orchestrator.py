"""
Main AI orchestration.

The application never requires Gemini:
Gemini -> Ollama (optional) -> built-in local generator.
Image generation:
Diffusers (optional) -> Pillow fallback.
"""
from typing import Tuple, List, Dict

from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.ollama_fallback import generate_outline_ollama, generate_story_ollama
from app.services.local_story import generate_local_outline, generate_local_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


def _outline(req) -> Tuple[List[Dict], str]:
    try:
        return generate_outline(
            req.story_prompt, req.character_name, req.setting,
            req.tone, req.art_style, req.panels
        ), "Gemini"
    except Exception:
        try:
            return generate_outline_ollama(
                req.story_prompt, req.character_name, req.setting,
                req.tone, req.art_style, req.panels
            ), "Ollama"
        except Exception:
            return generate_local_outline(
                req.story_prompt, req.character_name, req.setting,
                req.tone, req.art_style, req.panels
            ), "Local fallback"


def _story(outline, req) -> Tuple[List[Dict], str]:
    try:
        return generate_story(outline, req.character_name, req.tone), "Gemini"
    except Exception:
        try:
            return generate_story_ollama(outline, req.character_name, req.tone), "Ollama"
        except Exception:
            return generate_local_story(outline, req.character_name, req.tone), "Local fallback"


def generate_comic(req):
    outline, outline_source = _outline(req)
    story, story_source = _story(outline, req)

    images = []
    for index, panel in enumerate(story, start=1):
        images.append(generate_image(panel["image_prompt"], index))

    layout = build_comic_layout(story, images)
    pdf_url = save_pdf(layout)

    if outline_source == "Gemini" and story_source == "Gemini":
        source = "Gemini + image pipeline"
        message = "Comic generated with Gemini."
    else:
        source = f"{outline_source} + {story_source} + local image fallback when needed"
        message = "Comic generated successfully. Gemini was unavailable or not configured, so fallback generation was used."

    return layout, pdf_url, source, message
