"""
Built-in deterministic story generator.

This is intentionally dependency-free so ComicCraft can still generate a usable
comic when Gemini and Ollama are unavailable.
"""
from typing import List, Dict


def _clean(value: str, default: str) -> str:
    value = (value or "").strip()
    return value if value else default


def generate_local_outline(story_prompt: str, character_name: str, setting: str,
                           tone: str, art_style: str, panels: int = 5) -> List[Dict]:
    story_prompt = _clean(story_prompt, "an unexpected adventure")
    character_name = _clean(character_name, "Alex")
    setting = _clean(setting, "a mysterious forest")
    tone = _clean(tone, "funny")
    art_style = _clean(art_style, "comic book")

    beats = [
        ("The Beginning", f"{character_name} discovers the first strange clue in {setting}."),
        ("The Mystery", f"The clue leads {character_name} deeper into {setting}, where something unexpected appears."),
        ("The Problem", f"{character_name} faces a challenge that makes the original plan much harder."),
        ("The Turning Point", f"{character_name} uses creativity and courage to solve the main problem."),
        ("The Ending", f"The adventure ends with a surprising result and a memorable final moment."),
        ("A New Clue", f"Just when everything seems finished, {character_name} notices another tiny mystery."),
        ("The Next Adventure", f"{character_name} decides that this cannot be the end of the story.")
    ]

    result = []
    for i in range(panels):
        title, scene = beats[i]
        result.append({
            "panel_number": i + 1,
            "title": title,
            "scene_description": (
                f"{scene} The story idea is: {story_prompt}. "
                f"Keep the mood {tone} and the visual language {art_style}."
            ),
            "image_prompt": (
                f"{art_style} comic panel, {character_name} as the main character, "
                f"{setting}, {scene}, visual storytelling, expressive face, dynamic composition, "
                f"clear foreground and background, family-friendly, no text, no watermark"
            ),
        })
    return result


def generate_local_story(outline: List[Dict], character_name: str, tone: str) -> List[Dict]:
    character_name = _clean(character_name, "Alex")
    tone = _clean(tone, "funny")

    dialogue_pool = {
        "funny": [
            "Okay... this was definitely not in the plan!",
            "I have a plan. It is a very small plan.",
            "Why does every adventure come with a surprise?",
            "That worked! I am going to pretend I meant to do that.",
            "Next time, I am bringing snacks."
        ],
        "dramatic": [
            "I have to keep going.",
            "There has to be another way.",
            "This is our moment.",
            "I cannot give up now.",
            "The journey has changed me."
        ],
        "light-hearted": [
            "This is going to be interesting!",
            "Come on, let's see where this goes.",
            "I think we can solve this.",
            "That was easier than I expected.",
            "What an adventure!"
        ],
        "poetic": [
            "Every path hides a new possibility.",
            "The quiet world seems to be speaking.",
            "Courage begins with one small step.",
            "Even a mystery can become a memory.",
            "The road ahead is still waiting."
        ],
    }
    pool = dialogue_pool.get(tone.lower(), dialogue_pool["funny"])

    enriched = []
    for idx, panel in enumerate(outline):
        item = dict(panel)
        item["caption"] = f"Panel {idx + 1}: The adventure continues."
        item["narration"] = (
            f"{character_name} takes in the scene and reacts to what is happening. "
            f"The moment pushes the story forward while keeping the {tone} tone."
        )
        item["dialogue"] = f'{character_name}: "{pool[idx % len(pool)]}"'
        enriched.append(item)
    return enriched
