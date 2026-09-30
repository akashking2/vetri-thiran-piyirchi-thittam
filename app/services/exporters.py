from pathlib import Path
from datetime import datetime
from typing import List, Dict
from fpdf import FPDF
import os

from app.config import BASE_DIR, EXPORTS_DIR


def _local_image_path(image_url: str) -> Path:
    # image_url is expected to be /static/panels/name.png
    relative = image_url.replace("/static/", "static/")
    return BASE_DIR / relative


def save_pdf(layout: List[Dict]) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comiccraft_{timestamp}.pdf"
    output = EXPORTS_DIR / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, f"Panel {panel.get('panel_number', '')}: {panel.get('title', '')}")

        image_path = _local_image_path(panel.get("image_path", ""))
        if image_path.exists():
            pdf.image(str(image_path), x=15, y=35, w=180)

        pdf.ln(105)
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 7, panel.get("scene_description", ""))

        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, panel.get("caption", ""))

        pdf.ln(2)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, panel.get("narration", ""))

        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, panel.get("dialogue", ""))

    pdf.output(str(output))
    return f"/static/exports/{filename}"
