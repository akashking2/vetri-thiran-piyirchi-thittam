from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from app.models import PromptRequest
from app.services.orchestrator import generate_comic
from app.services.image_generator import generate_image
from app.services.exporters import save_pdf

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return request.app.state.templates.TemplateResponse(
        request, "index.html"
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Alex"),
    setting: str = Form("forest"),
    tone: str = Form("funny"),
    art_style: str = Form("comic book"),
    panels: int = Form(5),
):
    try:
        req = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
            panels=panels,
        )
        layout, pdf_url, source, message = generate_comic(req)
        return request.app.state.templates.TemplateResponse(
            request,
            "comic_preview.html",
            {
                "layout": layout,
                "pdf_url": pdf_url,
                "source": source,
                "message": message,
            },
        )
    except Exception as exc:
        return request.app.state.templates.TemplateResponse(
            request,
            "error.html",
            {"error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_comic_json(req: PromptRequest):
    try:
        layout, pdf_url, source, message = generate_comic(req)
        return JSONResponse({
            "success": True,
            "source": source,
            "message": message,
            "layout": layout,
            "pdf_url": pdf_url,
        })
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    try:
        path = generate_image(prompt, 999)
        return {"success": True, "image_path": path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    from app.config import EXPORTS_DIR
    file_path = EXPORTS_DIR / filename
    if not file_path.exists() or file_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_path.name,
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return request.app.state.templates.TemplateResponse(
        request, "export_success.html"
    )
