from __future__ import annotations
from typing import List, Tuple
from .evidence_io import Evidence


def quoted_evidence(evs: List[Evidence]) -> List[str]:
    quotes: List[str] = []
    for e in evs:
        frag = e.fragment.strip()
        if len(frag) > 300:
            frag = frag[:297] + "…"
        quotes.append(f"{frag}")
    return quotes


def package_outputs(case_id: str, assessment_json: dict, friendly_text: str) -> dict:
    return {
        "case_id": case_id,
        "clinical_json": assessment_json,
        "patient_text": friendly_text,
    }