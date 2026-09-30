"""Comic image generation service.

Priority:
1. Hugging Face Diffusers + Stable Diffusion when HF_TOKEN is configured.
2. A richer Pillow comic renderer when AI image generation is unavailable.

The Pillow fallback intentionally creates different compositions for each panel
instead of drawing the same placeholder scene repeatedly.
"""
import hashlib
import os
import re
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from app.config import PANELS_DIR, HF_TOKEN, IMAGE_MODEL

_PIPE = None


def _safe_name(prompt: str, index: int) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", prompt.lower()).strip("_")[:45]
    digest = hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:10]
    return f"panel_{index}_{slug}_{digest}.png"


def _font(size: int):
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _theme(prompt: str):
    p = prompt.lower()
    if any(x in p for x in ["space", "galaxy", "planet", "rocket"]):
        return "space"
    if any(x in p for x in ["forest", "jungle", "village", "mountain", "magical"]):
        return "nature"
    if any(x in p for x in ["school", "classroom", "library", "student"]):
        return "school"
    if any(x in p for x in ["city", "street", "future", "robot"]):
        return "city"
    if any(x in p for x in ["ocean", "sea", "beach", "island"]):
        return "ocean"
    return "adventure"


def _background(draw, theme: str, panel: int, w: int, h: int):
    palettes = {
        "space": [(24, 31, 70), (35, 52, 110), (12, 18, 45), (70, 50, 100), (20, 70, 80)],
        "nature": [(210, 235, 205), (185, 220, 180), (230, 210, 165), (195, 225, 235), (220, 205, 175)],
        "school": [(235, 225, 205), (220, 230, 240), (240, 215, 195), (215, 230, 215), (235, 225, 240)],
        "city": [(190, 215, 235), (205, 205, 220), (225, 205, 185), (175, 200, 215), (220, 210, 195)],
        "ocean": [(175, 220, 235), (155, 205, 225), (190, 225, 215), (160, 215, 225), (200, 220, 230)],
        "adventure": [(225, 220, 195), (205, 220, 235), (230, 205, 185), (205, 225, 205), (225, 210, 225)],
    }
    bg = palettes[theme][(panel - 1) % len(palettes[theme])]
    draw.rectangle((0, 0, w, h), fill=bg)

    # Panel-specific establishing details.
    if theme == "space":
        for i in range(30):
            x = (i * 137 + panel * 43) % w
            y = 180 + (i * 79 + panel * 31) % 430
            r = 1 + (i % 3)
            draw.ellipse((x-r, y-r, x+r, y+r), fill="white")
        draw.ellipse((760, 210, 900, 350), fill=(215, 220, 245), outline="black", width=4)
    elif theme == "nature":
        draw.rectangle((0, 555, w, h), fill=(110, 165, 105))
        for x in range(-40, w + 80, 120):
            draw.polygon([(x, 555), (x + 55, 360), (x + 110, 555)], fill=(65, 120, 80), outline="black")
        draw.ellipse((730, 115, 865, 250), fill=(250, 220, 120), outline="black", width=3)
    elif theme == "school":
        draw.rectangle((0, 500, w, h), fill=(150, 105, 70))
        for x in [100, 350, 600, 850]:
            draw.rectangle((x, 380, x + 150, 500), fill=(195, 145, 85), outline="black", width=4)
        draw.rectangle((310, 205, 715, 330), fill=(225, 235, 220), outline="black", width=5)
    elif theme == "city":
        draw.rectangle((0, 515, w, h), fill=(85, 85, 95))
        buildings = [(20, 260, 170, 515), (190, 320, 350, 515), (370, 220, 555, 515), (580, 290, 730, 515), (760, 245, 970, 515)]
        for x1, y1, x2, y2 in buildings:
            draw.rectangle((x1, y1, x2, y2), fill=(145, 155, 170), outline="black", width=4)
            for wx in range(x1 + 20, x2 - 10, 40):
                for wy in range(y1 + 30, y2 - 20, 55):
                    draw.rectangle((wx, wy, wx + 16, wy + 25), fill=(245, 225, 130), outline="black")
    elif theme == "ocean":
        draw.rectangle((0, 450, w, h), fill=(55, 150, 190))
        for y in [480, 535, 590, 645]:
            draw.arc((0, y - 25, w, y + 25), 180, 360, fill="white", width=3)
        draw.polygon([(70, 620), (250, 430), (430, 620)], fill=(210, 185, 120), outline="black")
    else:
        draw.rectangle((0, 545, w, h), fill=(170, 145, 105))
        draw.ellipse((760, 120, 900, 260), fill=(250, 215, 120), outline="black", width=4)


def _character(draw, x: int, y: int, scale: float = 1.0, pose: str = "stand", accent="black"):
    # Simple reusable character with changing poses; deliberately more expressive
    # than the previous identical smiley-face placeholder.
    s = scale
    head_r = int(48 * s)
    body_w = int(70 * s)
    body_h = int(105 * s)
    draw.ellipse((x-head_r, y-head_r, x+head_r, y+head_r), fill=(245, 205, 170), outline="black", width=max(2, int(5*s)))
    # hair
    draw.arc((x-head_r, y-head_r-8, x+head_r, y+head_r+25), 185, 355, fill=accent, width=max(4, int(10*s)))
    # eyes
    er = max(2, int(5*s))
    draw.ellipse((x-18*s-er, y-8*s-er, x-18*s+er, y-8*s+er), fill="black")
    draw.ellipse((x+18*s-er, y-8*s-er, x+18*s+er, y-8*s+er), fill="black")
    if pose == "surprised":
        draw.ellipse((x-10*s, y+10*s, x+10*s, y+30*s), outline="black", width=max(2, int(4*s)))
    elif pose == "happy":
        draw.arc((x-22*s, y+4*s, x+22*s, y+35*s), 10, 170, fill="black", width=max(2, int(4*s)))
    else:
        draw.line((x-16*s, y+20*s, x+16*s, y+20*s), fill="black", width=max(2, int(3*s)))
    # body and clothes
    top = y + head_r
    draw.rounded_rectangle((x-body_w//2, top, x+body_w//2, top+body_h), radius=int(14*s), fill=(80, 125, 190), outline="black", width=max(2, int(4*s)))
    if pose == "run":
        draw.line((x-20*s, top+body_h, x-65*s, top+body_h+55*s), fill="black", width=max(3, int(6*s)))
        draw.line((x+20*s, top+body_h, x+60*s, top+body_h+25*s), fill="black", width=max(3, int(6*s)))
        draw.line((x-body_w//2, top+35*s, x-75*s, top-15*s), fill="black", width=max(3, int(6*s)))
        draw.line((x+body_w//2, top+35*s, x+75*s, top-25*s), fill="black", width=max(3, int(6*s)))
    elif pose == "point":
        draw.line((x+body_w//2, top+30*s, x+85*s, top-25*s), fill="black", width=max(3, int(6*s)))
        draw.line((x-body_w//2, top+35*s, x-50*s, top+80*s), fill="black", width=max(3, int(6*s)))
        draw.line((x-20*s, top+body_h, x-50*s, top+60*s+body_h), fill="black", width=max(3, int(6*s)))
        draw.line((x+20*s, top+body_h, x+50*s, top+60*s+body_h), fill="black", width=max(3, int(6*s)))
    else:
        draw.line((x-22*s, top+body_h, x-38*s, top+75*s+body_h), fill="black", width=max(3, int(6*s)))
        draw.line((x+22*s, top+body_h, x+38*s, top+75*s+body_h), fill="black", width=max(3, int(6*s)))
        draw.line((x-body_w//2, top+35*s, x-70*s, top+70*s), fill="black", width=max(3, int(6*s)))
        draw.line((x+body_w//2, top+35*s, x+70*s, top+70*s), fill="black", width=max(3, int(6*s)))


def _speech(draw, x, y, text, width=330):
    font = _font(21)
    words = re.sub(r"\s+", " ", text).strip().split()
    lines, line = [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= width - 35:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    lines = lines[:4]
    height = 35 + len(lines) * 27
    draw.rounded_rectangle((x, y, x + width, y + height), radius=18, fill="white", outline="black", width=4)
    draw.polygon([(x + 50, y + height), (x + 85, y + height), (x + 68, y + height + 30)], fill="white", outline="black")
    for i, line in enumerate(lines):
        draw.text((x + 18, y + 13 + i * 27), line, fill="black", font=font)


def _fallback_image(prompt: str, index: int) -> str:
    filename = _safe_name(prompt, index)
    path = PANELS_DIR / filename
    w, h = 1024, 768
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)

    theme = _theme(prompt)
    _background(draw, theme, index, w, h)

    # Strongly different composition for each panel.
    if index % 5 == 1:
        # Establishing shot: character small, environment large.
        _character(draw, 270, 390, 0.85, "stand")
        draw.text((70, 85), "THE BEGINNING", fill="black", font=_font(32))
        _speech(draw, 470, 170, "Something strange is happening here...", 390)
    elif index % 5 == 2:
        # Close-up / discovery.
        _character(draw, 360, 400, 1.55, "surprised", "black")
        draw.rounded_rectangle((600, 350, 850, 550), radius=25, fill=(245, 235, 160), outline="black", width=6)
        draw.text((650, 405), "NEW\nDISCOVERY", fill="black", font=_font(28))
        _speech(draw, 80, 165, "Wait... what is that?", 360)
    elif index % 5 == 3:
        # Action / movement.
        _character(draw, 470, 330, 1.1, "run")
        for i in range(5):
            y = 230 + i * 65
            draw.line((100 + i * 30, y, 300 + i * 30, y), fill="black", width=5)
        draw.polygon([(720, 260), (850, 350), (720, 440)], fill=(245, 180, 70), outline="black")
        draw.text((710, 470), "WHOOSH!", fill="black", font=_font(34))
    elif index % 5 == 4:
        # Two-character interaction / decision.
        _character(draw, 285, 365, 0.95, "point")
        _character(draw, 700, 365, 0.95, "stand")
        draw.line((380, 470, 610, 470), fill="black", width=5)
        _speech(draw, 90, 130, "We need a plan.", 300)
        _speech(draw, 600, 130, "I have an idea!", 320)
    else:
        # Climax / victory wide shot.
        _character(draw, 510, 335, 1.2, "happy")
        draw.ellipse((350, 170, 670, 490), outline="black", width=7)
        for a in range(0, 360, 45):
            import math
            x1 = 510 + int(190 * math.cos(math.radians(a)))
            y1 = 330 + int(190 * math.sin(math.radians(a)))
            x2 = 510 + int(260 * math.cos(math.radians(a)))
            y2 = 330 + int(260 * math.sin(math.radians(a)))
            draw.line((x1, y1, x2, y2), fill="black", width=6)
        draw.text((370, 560), "THE ADVENTURE CONTINUES!", fill="black", font=_font(30))
        _speech(draw, 70, 125, "We did it!", 270)

    # Footer contains a readable prompt reference, but not as the main artwork.
    words = re.sub(r"\s+", " ", prompt).strip()
    if len(words) > 105:
        words = words[:102] + "..."
    draw.rectangle((45, 690, 979, 745), fill="white", outline="black", width=2)
    draw.text((62, 705), words, fill="black", font=_font(18))
    draw.rectangle((25, 25, 999, 743), outline="black", width=8)
    draw.text((45, 45), f"COMICCRAFT — PANEL {index}", fill="black", font=_font(27))

    img.save(path)
    return f"/static/panels/{filename}"


def _try_diffusers(prompt: str, index: int) -> Optional[str]:
    global _PIPE
    if not HF_TOKEN:
        return None
    try:
        import torch
        from diffusers import StableDiffusionPipeline
        if _PIPE is None:
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            _PIPE = StableDiffusionPipeline.from_pretrained(
                IMAGE_MODEL,
                torch_dtype=dtype,
                token=HF_TOKEN,
            )
            if torch.cuda.is_available():
                _PIPE = _PIPE.to("cuda")
        # Add panel number to reduce repeated compositions.
        enhanced = f"comic panel {index}, dynamic composition, {prompt}"
        image = _PIPE(
            enhanced,
            num_inference_steps=20,
            guidance_scale=7.0,
            height=512,
            width=768,
        ).images[0]
        filename = _safe_name(prompt, index)
        path = PANELS_DIR / filename
        image.save(path)
        return f"/static/panels/{filename}"
    except Exception:
        return None


def generate_image(prompt: str, index: int = 1) -> str:
    generated = _try_diffusers(prompt, index)
    return generated or _fallback_image(prompt, index)
