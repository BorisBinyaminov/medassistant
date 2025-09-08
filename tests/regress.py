from __future__ import annotations
import json
from pathlib import Path
from bot.config import settings
from bot.evidence_io import Evidence, append_evidence
from bot.handoff import quoted_evidence
from bot.reviewer import analyze_case
from bot.utils import now_iso

CASES_DIR = Path("tests/cases")
OUT_DIR = settings.compare_dir


def run_one(case_path: Path):
    case = json.loads(case_path.read_text(encoding="utf-8"))
    case_id = case["case_id"]
    user_id = case.get("user_id", 0)

    evs = []
    if txt := case["inputs"].get("text"):
        evs.append(Evidence(case_id, user_id, "patient_text", txt, {"type": "test"}, now_iso()))
    if labs := case["inputs"].get("labs"):
        evs.append(Evidence(case_id, user_id, "lab", labs, {"type": "test"}, now_iso()))
    append_evidence(evs)

    quotes = quoted_evidence(evs)
    assessment = analyze_case(case_id, quotes)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{case_id}.json").write_text(json.dumps(assessment, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    for p in CASES_DIR.glob("*.json"):
        run_one(p)
    print(f"Done. See {OUT_DIR}")

if __name__ == "__main__":
    main()