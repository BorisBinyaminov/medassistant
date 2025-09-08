from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
from PIL import Image
import pdfplumber
import pytesseract
from .utils import normalize_text


def ocr_image(path: Path) -> str:
    img = Image.open(path)
    text = pytesseract.image_to_string(img, lang="eng+rus")  # extend langs as needed
    return normalize_text(text)


def parse_pdf(path: Path) -> Tuple[str, List[Tuple[int, str]]]:
    """Return (full_text, per_page list[(page_index, text)])
    Uses embedded text if present; falls back to OCR per page when empty.
    """
    full = []
    per_page: List[Tuple[int, str]] = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            t = page.extract_text() or ""
            if not t.strip():
                # OCR rasterized page
                img = page.to_image(resolution=300).original  # PIL image
                t = pytesseract.image_to_string(img, lang="eng+rus")
            t = normalize_text(t)
            per_page.append((i + 1, t))
            full.append(t)
    return normalize_text("\n\n".join(full)), per_page