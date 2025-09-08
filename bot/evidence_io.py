from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional
from bot import config

@dataclass
class Evidence:
    case_id: str
    user_id: int
    role: str  # "patient_text" | "ocr" | "lab" | "system"
    fragment: str
    source: dict  # {type, file_name?, page?, bbox?, hash?, note?}
    created_at: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def append_evidence(records: Iterable[Evidence], db_path: Path | None = None) -> None:
    db = db_path or config.DB_PATH
    db.parent.mkdir(parents=True, exist_ok=True)
    with db.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(r.to_json() + "\n")


def load_evidence(case_id: str, user_id: int, db_path: Path | None = None) -> List[Evidence]:
    db = db_path or config.DB_PATH
    out: List[Evidence] = []
    if not db.exists():
        return out
    with db.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
            except Exception:
                continue
            if row.get("case_id") == case_id and row.get("user_id") == user_id:
                out.append(Evidence(**row))
    return out