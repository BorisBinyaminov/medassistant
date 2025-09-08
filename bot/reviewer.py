# bot/reviewer.py
from __future__ import annotations
import json, re, logging
from typing import List
import httpx
from openai import OpenAI
from bot import config
from .prompts import SYSTEM_REASONING, SYSTEM_FRIENDLY

log = logging.getLogger("reviewer")

# Стабильный HTTP-клиент: без HTTP/2 и keep-alive (меньше проблем с сетями/прокси)
transport = httpx.HTTPTransport(http2=False)
_httpx = httpx.Client(
    transport=transport,
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=0, max_connections=5),
    headers={"Connection": "close"},
)

_client = OpenAI(
    api_key=(config.OPENAI_API_KEY or "").strip(),
    base_url=(config.OPENAI_BASE_URL or "https://api.openai.com/v1").strip(),
    http_client=_httpx,
)

# ✅ Дефолты на случай, если в окружении пусто
MODEL_REASONING = (getattr(config, "MODEL_REASONING", "") or "gpt-4o-mini").strip()
MODEL_FRIENDLY  = (getattr(config, "MODEL_FRIENDLY", "")  or "gpt-4o-mini").strip()

def _ensure_model(name: str, kind: str) -> str:
    if not name:
        raise RuntimeError(f"Empty model name for {kind}")
    return name

def _strict_json_from_text(text: str) -> dict:
    """Пытаемся распарсить чистый JSON, иначе — берём последнюю { ... }-структуру."""
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}$", text)
        if m:
            return json.loads(m.group(0))
        raise RuntimeError(f"Model did not return valid JSON:\n{text}")

def analyze_case(case_id: str, evidence_quotes: List[str]) -> dict:
    prompt = (
        "You will receive quoted evidence snippets for a single case.\n"
        "Return ONLY valid JSON per the provided schema. Do not add prose.\n\n"
        f"Case: {case_id}\n"
        "Evidence:\n- " + "\n- ".join(evidence_quotes)
    )
    model = _ensure_model(MODEL_REASONING, "reasoning")
    log.debug("analyze_case → model=%s", model)

    try:
        res = _client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_REASONING},
                {"role": "user", "content": prompt},
            ],
            timeout=30,
        )
        text = res.output_text or ""
        return _strict_json_from_text(text)
    except Exception as e:
        log.exception("analyze_case failed: %s", e)
        raise

def friendly_message(json_assessment: dict) -> str:
    """Форматирует пациенту/врачу через Responses API."""
    content = json.dumps(json_assessment, ensure_ascii=False)
    prompt = (
        "Convert the following strict JSON clinical assessment into:\n"
        "1) A friendly message for the patient (short, plain language).\n"
        "2) A concise clinician note (bullet points).\n\n"
        f"JSON:\n```json\n{content}\n```"
    )
    model = _ensure_model(MODEL_FRIENDLY, "friendly")
    log.debug("friendly_message → model=%s", model)

    try:
        res = _client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_FRIENDLY},
                {"role": "user", "content": prompt},
            ],
            timeout=30,
        )
        return res.output_text or ""
    except Exception as e:
        log.exception("friendly_message failed: %s", e)
        # вернём короткое сообщение вместо падения хендлера
        return "Не удалось сформировать читабельное резюме ответа. Попробуйте ещё раз позже."
