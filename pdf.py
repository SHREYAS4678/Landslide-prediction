"""PDF extraction — research papers → structured threshold data."""
import re, io
from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter()

def _extract_with_pdfplumber(content: bytes) -> list[dict]:
    try:
        import pdfplumber
        result = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            full_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        result = _parse_thresholds(full_text)
        return result
    except ImportError:
        raise HTTPException(500, "pdfplumber not installed. Add it to requirements.txt")

def _parse_thresholds(text: str) -> list[dict]:
    """Regex-based extraction of common landslide threshold patterns."""
    items = []
    patterns = [
        (r"rainfall[^\d]*(\d+\.?\d*)\s*mm", "threshold_rainfall_mm"),
        (r"soil moisture[^\d]*(\d+\.?\d*)\s*%", "critical_soil_moisture_pct"),
        (r"slope angle[^\d]*(\d+\.?\d*)\s*°", "slope_failure_angle_deg"),
        (r"vibration[^\d]*(\d+\.?\d*)\s*[Gg]", "seismic_trigger_g"),
        (r"saturation[^\d]*(\d+\.?\d*)\s*%", "saturation_threshold_pct"),
    ]
    for pattern, label in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            items.append({"field": label, "values": matches[:5], "source": "regex"})
    return items

@router.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    """Upload a PDF research paper and extract landslide threshold values."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(413, "File too large (max 20 MB)")
    extracted = _extract_with_pdfplumber(content)
    return {
        "filename": file.filename,
        "size_kb": round(len(content) / 1024, 1),
        "items_found": len(extracted),
        "data": extracted,
    }
