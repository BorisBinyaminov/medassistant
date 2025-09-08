# MedAssistant GPT-5 Telegram Bot — Starter Kit

Compact, end-to-end starter you can run and extend. Files are grouped by paths. Replace placeholders in `.env`.

---

## bot/__init__.py
```python
# empty on purpose (package initializer)
```

## bot/config.py
```python
from pydantic import BaseSettings, Field
from pathlib import Path

class Settings(BaseSettings):
    # Telegram
    telegram_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")

    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_org: str | None = Field(None, env="OPENAI_ORG")

    # Models
    model_reasoning: str = Field("gpt-5", env="MODEL_REASONING")
    model_friendly: str = Field("gpt-5-chat", env="MODEL_FRIENDLY")

    # Paths
    root_dir: Path = Path(__file__).resolve().parents[1]
    artifacts_dir: Path = root_dir / "artifacts"
    db_path: Path = artifacts_dir / "db" / "evidence.jsonl"
    compare_dir: Path = artifacts_dir / "compare"

    # Runtime
    debug: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"

settings = Settings()
settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
(settings.artifacts_dir / "db").mkdir(parents=True, exist_ok=True)
settings.compare_dir.mkdir(parents=True, exist_ok=True)
```

## bot/utils.py
```python
import hashlib
import re
import uuid
from datetime import datetime
from typing import Iterable

WHITESPACE_RE = re.compile(r"\s+", re.MULTILINE)


def normalize_text(s: str) -> str:
    s = s.replace("\u00A0", " ")  # nbsp
    s = WHITESPACE_RE.sub(" ", s)
    return s.strip()


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def new_case_id(prefix: str = "case") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def chunks(it: Iterable, n: int):
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) == n:
            yield buf
            buf = []
    if buf:
        yield buf
```

## bot/evidence_io.py
```python
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional
from .config import settings

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
    db = db_path or settings.db_path
    db.parent.mkdir(parents=True, exist_ok=True)
    with db.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(r.to_json() + "\n")


def load_evidence(case_id: str, user_id: int, db_path: Path | None = None) -> List[Evidence]:
    db = db_path or settings.db_path
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
```

## bot/ocr.py
```python
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
```

## bot/lab_extract.py
```python
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
```

## bot/prompts.py
```python
SYSTEM_REASONING = (
    "You are MedAssistant, a careful clinical reasoning model. "
    "Given a case with evidence snippets (labs, HPI, findings), "
    "produce differential diagnoses, red flags, and triage recommendations. "
    "Be explicit about uncertainty. Cite evidence by quoting short phrases. "
    "Return STRICT JSON per the schema."
)

SCHEMA_JSON = {
    "type": "object",
    "properties": {
        "case_id": {"type": "string"},
        "summary": {"type": "string"},
        "triage": {"type": "string", "enum": ["emergent", "urgent", "routine"]},
        "differential": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "dx": {"type": "string"},
                    "likelihood": {"type": "string"},
                    "rationale": {"type": "string"},
                    "evidence_quotes": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["dx", "rationale", "evidence_quotes"],
                "additionalProperties": False,
            },
        },
        "red_flags": {"type": "array", "items": {"type": "string"}},
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["case_id", "summary", "triage", "differential", "red_flags", "next_steps"],
    "additionalProperties": False,
}

SYSTEM_FRIENDLY = (
    "You are a friendly clinician communicator. Convert the JSON assessment "
    "into a readable message for a patient and a separate concise note for a clinician."
)
```

## bot/reviewer.py
```python
from __future__ import annotations
import json
from typing import List
# pip install openai>=1.0.0
from openai import OpenAI
from .config import settings
from .prompts import SYSTEM_REASONING, SYSTEM_FRIENDLY

_client = OpenAI(api_key=settings.openai_api_key, organization=settings.openai_org)


def analyze_case(case_id: str, evidence_quotes: List[str]) -> dict:
    """Call GPT-5 (responses API) to produce STRICT JSON clinical output."""
    prompt = (
        "You will receive quoted evidence snippets for a single case.\n"
        "Return ONLY valid JSON per the provided schema. Do not add prose.\n\n"
        f"Case: {case_id}\n"
        "Evidence:\n- " + "\n- ".join(evidence_quotes)
    )

    # Using Responses API (tool-free basic call)
    result = _client.responses.create(
        model=settings.model_reasoning,
        input=[
            {"role": "system", "content": SYSTEM_REASONING},
            {"role": "user", "content": prompt},
        ],
        # Optionally: response_format={"type": "json_object"}
    )

    text = result.output_text
    try:
        return json.loads(text)
    except Exception as e:
        # Best-effort recovery: try to extract JSON block
        import re
        m = re.search(r"\{[\s\S]*\}$", text)
        if m:
            return json.loads(m.group(0))
        raise RuntimeError(f"Model did not return valid JSON: {e}\n{text}")


def friendly_message(json_assessment: dict) -> str:
    """Optionally format a patient-friendly message via chat completions."""
    content = json.dumps(json_assessment, ensure_ascii=False)
    resp = _client.chat.completions.create(
        model=settings.model_friendly,
        messages=[
            {"role": "system", "content": SYSTEM_FRIENDLY},
            {"role": "user", "content": f"Format this assessment: ```json\n{content}\n```"},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content
```

## bot/handoff.py
```python
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
```

## bot/main.py
```python
from __future__ import annotations
import asyncio
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ContentType
from .config import settings
from .utils import new_case_id, now_iso, normalize_text, sha256_of
from .ocr import ocr_image, parse_pdf
from .lab_extract import extract_panels
from .evidence_io import Evidence, append_evidence, load_evidence
from .handoff import quoted_evidence, package_outputs
from .reviewer import analyze_case, friendly_message

bot = Bot(token=settings.telegram_token, parse_mode="HTML")
dp = Dispatcher()

@dp.message(CommandStart())
async def on_start(m: Message):
    await m.answer(
        "Привет! Пришлите симптомы в тексте и/или загрузите анализы (PDF/JPG/PNG).\n"
        "Я соберу доказательства и дам клиническое резюме."
    )

@dp.message(F.content_type == ContentType.TEXT)
async def on_text(m: Message):
    case_id = new_case_id()
    user_id = m.from_user.id
    text = normalize_text(m.text or "")
    ev = Evidence(
        case_id=case_id,
        user_id=user_id,
        role="patient_text",
        fragment=text,
        source={"type": "telegram_text", "message_id": m.message_id},
        created_at=now_iso(),
    )
    append_evidence([ev])
    await m.answer(f"✅ Текст добавлен к делу <code>{case_id}</code>. Теперь можно прислать файлы или написать /review {case_id}")

@dp.message(F.content_type.in_({ContentType.DOCUMENT, ContentType.PHOTO}))
async def on_file(m: Message):
    case_id = new_case_id()
    user_id = m.from_user.id

    # Download file
    if m.photo:
        file = await bot.get_file(m.photo[-1].file_id)
        suffix = ".jpg"
    else:
        file = await bot.get_file(m.document.file_id)
        suffix = Path(m.document.file_name or "file").suffix or ".bin"
    dest = Path("artifacts") / f"upload_{case_id}{suffix}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    await bot.download_file(file.file_path, destination=dest)

    raw = dest.read_bytes()
    source_meta = {"type": "upload", "path": str(dest), "sha256": sha256_of(raw)}

    fragments = []
    if dest.suffix.lower() == ".pdf":
        full, per_page = parse_pdf(dest)
        fragments.append(("ocr", full, {**source_meta}))
        for page_idx, page_text in per_page:
            fragments.append(("ocr", page_text, {**source_meta, "page": page_idx}))
    else:
        text = ocr_image(dest)
        fragments.append(("ocr", text, source_meta))

    # Extract labs (primitive)
    lab_hits = []
    for _, frag, _ in fragments:
        lab_hits.extend(extract_panels(frag))
    if lab_hits:
        lab_text = "; ".join([f"{k}={v}" for k, v in lab_hits])
        fragments.append(("lab", lab_text, {"type": "lab_extract"}))

    evs = [
        Evidence(
            case_id=case_id,
            user_id=user_id,
            role=role,
            fragment=frag,
            source=meta,
            created_at=now_iso(),
        )
        for role, frag, meta in fragments
    ]
    append_evidence(evs)

    await m.answer(f"📄 Файл обработан и добавлен к делу <code>{case_id}</code>. Напишите /review {case_id} когда будете готовы.")

@dp.message(F.text.startswith("/review"))
async def on_review(m: Message):
    parts = (m.text or "").split()
    if len(parts) < 2:
        return await m.answer("Укажите: /review &lt;case_id&gt;")
    case_id = parts[1].strip()
    user_id = m.from_user.id
    evs = load_evidence(case_id, user_id)
    if not evs:
        return await m.answer("Не нашёл доказательств для этого дела. Пришлите текст/файлы сначала.")

    quotes = quoted_evidence(evs)
    await m.answer("🧠 Анализирую кейс…")
    assessment = analyze_case(case_id, quotes)
    friendly = friendly_message(assessment)
    pkg = package_outputs(case_id, assessment, friendly)

    # Minimal render
    await m.answer(
        "<b>Клиническое резюме</b>\n" +
        friendly +
        f"\n\n<code>JSON:</code> <pre language=\"json\">{pkg['clinical_json']}</pre>"
    )


def run() -> None:
    import logging
    logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    run()
```

## bot/reviewer.py (optional streaming variant)
```python
# For later: add streaming to show partial progress in chat
```

## tests/cases/example_case.json
```json
{
  "case_id": "case_demo_001",
  "user_id": 12345,
  "inputs": {
    "text": "Мужчина 45 лет, боль в груди при нагрузке, длится 10 минут, иррадиирует в левую руку.",
    "labs": "CRP 2 mg/L, Hb 135 g/L"
  },
  "expect": {
    "triage": "urgent",
    "must_include": ["нестабильная стенокардия", "ЭКГ"],
    "must_flag": ["боль в груди"]
  }
}
```

## scripts/regress.py
```python
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
```

## docker/Dockerfile
```dockerfile
FROM python:3.11-slim

# System deps for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    libgl1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml poetry.lock* requirements.txt* /app/

# Use pip by default for simplicity
RUN pip install --no-cache-dir -r requirements.txt || true

COPY . /app

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "bot.main"]
```

## docker-compose.yml
```yaml
version: "3.9"
services:
  medassistant:
    build: ./docker
    env_file:
      - .env
    volumes:
      - ./:/app
    restart: unless-stopped
```

## requirements.txt
```text
aiogram>=3.6
openai>=1.40
pydantic>=2.7
pillow>=10.3
pdfplumber>=0.11
pytesseract>=0.3
```

## .env.example
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
OPENAI_API_KEY=sk-...
OPENAI_ORG=
MODEL_REASONING=gpt-5
MODEL_FRIENDLY=gpt-5-chat
DEBUG=false
```

---

### Evidence JSONL format (one line per fragment)
```json
{"case_id":"case_xxx","user_id":111,"role":"ocr","fragment":"Hb 130 g/L ...","source":{"type":"upload","path":"artifacts/upload_case_xxx.pdf","page":1,"sha256":"..."},"created_at":"2025-09-08T08:00:00Z"}
```

### Flow
1. User sends text/files → stored as `Evidence` fragments.
2. Optional lab regex pass adds derived fragments.
3. `/review <case_id>` → gather quotes → GPT‑5 responses API → strict JSON.
4. Optional friendly formatting via `gpt-5-chat`.
5. Handoff returns `{case_id, clinical_json, patient_text}`; render in chat and/or forward downstream.

### Notes
- Keep regex simple; rely on the model for reasoning.
- Strict JSON: we enforce with post-parse guard and minimal recovery.
- Add rate limiting and auth later if needed.
- For PHI, ensure encrypted storage and access control in production.

