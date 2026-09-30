from typing import List
from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=3, max_length=2000)
    character_name: str = Field(default="Alex", max_length=80)
    setting: str = Field(default="forest", max_length=120)
    tone: str = Field(default="funny", max_length=80)
    art_style: str = Field(default="comic book", max_length=80)
    panels: int = Field(default=5, ge=3, le=8)


class Panel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    caption: str = ""
    narration: str = ""
    dialogue: str = ""


class ComicResponse(BaseModel):
    success: bool
    source: str
    message: str
    layout: List[Panel]
    pdf_url: str | None = None
