# ComicCraft — AI Comic Story Creator

This implementation follows the supplied project specification: FastAPI + Jinja2,
panel-by-panel comic generation, images, layout, and PDF export.

## Important design change

Gemini is OPTIONAL.

Text fallback chain:
1. Gemini
2. Ollama, if installed/running
3. Built-in local generator

Image fallback chain:
1. Hugging Face Diffusers/Stable Diffusion, only when configured
2. Pillow local comic renderer

Therefore the application can run without a Gemini API key.

## Windows setup

```powershell
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## Gemini mode

Put this in `.env`:

GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash

Then restart Uvicorn.

## Optional Ollama mode

Install Ollama separately, pull a small model, and start Ollama:

```powershell
ollama pull llama3.2:3b
ollama serve
```

The app will automatically try Ollama if Gemini fails.

## Optional Stable Diffusion

Stable Diffusion is intentionally not in the default requirements because it can be
large and GPU-dependent. To enable it, install compatible versions of:

```powershell
pip install torch diffusers transformers accelerate safetensors
```

Set:

HF_TOKEN=your_huggingface_token

If Diffusers fails for any reason, Pillow fallback images are used.

## JSON API

POST `/generate-comic/json`:

```json
{
  "story_prompt": "A brave fox exploring an enchanted forest",
  "character_name": "Foxy",
  "setting": "forest",
  "tone": "funny",
  "art_style": "comic book",
  "panels": 5
}
```

## Image test

POST `/test-image` with a form field named `prompt`.

## Project structure

```text
ComicCraft/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── models.py
│   ├── config.py
│   └── services/
│       ├── gemini_flash.py
│       ├── gemini_pro.py
│       ├── ollama_fallback.py
│       ├── local_story.py
│       ├── image_generator.py
│       ├── layout_builder.py
│       ├── exporters.py
│       └── orchestrator.py
├── templates/
├── static/
├── .env.example
├── requirements.txt
└── README.md
```
