from __future__ import annotations
import re
from typing import Dict, List, Tuple
from .utils import normalize_text

# Very primitive patterns — extend per your lab formats
PATTERNS = {
    "cbc": re.compile(r"\b(Hb|Hemoglobin|Гемоглобин)\s*[:=]?\s*(\d+[\.,]?\d*)\b", re.I),
    "crp": re.compile(r"\b(CRP|СРБ)\s*[:=]?\s*(\d+[\.,]?\d*)\b", re.I),
    "creatinine": re.compile(r"\b(Creatinine|Креатинин)\s*[:=]?\s*(\d+[\.,]?\d*)\b", re.I),
}


def extract_panels(text: str) -> List[Tuple[str, str]]:
    text = normalize_text(text)
    hits: List[Tuple[str, str]] = []
    for name, rx in PATTERNS.items():
        for m in rx.finditer(text):
            hits.append((name, m.group(2).replace(",", ".")))
    return hits