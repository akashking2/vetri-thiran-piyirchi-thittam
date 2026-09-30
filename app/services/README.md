# Service modules

- `gemini_flash.py`: Gemini structured outline generation.
- `gemini_pro.py`: Gemini narration/dialogue generation.
- `ollama_fallback.py`: optional local LLM fallback.
- `local_story.py`: dependency-free fallback, always available.
- `image_generator.py`: optional Stable Diffusion plus local Pillow fallback.
- `layout_builder.py`: combines panels and image paths.
- `exporters.py`: creates the PDF.
- `orchestrator.py`: controls the fallback chain.
