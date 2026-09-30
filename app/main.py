from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import STATIC_DIR, TEMPLATES_DIR
from app.routes import router

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Gemini-optional AI comic generator with local fallbacks.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.state.templates = templates
app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "gemini_optional": True,
        "message": "ComicCraft is running. AI fallback chain is enabled."
    }
