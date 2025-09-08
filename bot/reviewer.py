# bot/reviewer.py
from __future__ import annotations
import json, re
from typing import List
import httpx
from openai import OpenAI
from bot import config
from .prompts import SYSTEM_REASONING, SYSTEM_FRIENDLY

transport = httpx.HTTPTransport(
    http2=False,       # выключаем HTTP/2
)

_httpx = httpx.Client(
    transport=transport,
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=0, max_connections=5),  # без keep-alive
    headers={"Connection": "close"},
)

_client = OpenAI(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_BASE_URL,
    http_client=_httpx,
)

def analyze_case(case_id: str, evidence_quotes: List[str]) -> dict:
    prompt = (
        "You will receive quoted evidence snippets for a single case.\n"
        "Return ONLY valid JSON per the provided schema. Do not add prose.\n\n"
        f"Case: {case_id}\n"
        "Evidence:\n- " + "\n- ".join(evidence_quotes)
    )
    res = _client.responses.create(
        model=config.MODEL_REASONING,
        input=[
            {"role": "system", "content": SYSTEM_REASONING},
            {"role": "user", "content": prompt},
        ],
        timeout=30,
    )
    text = res.output_text
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}$", text)
        if m:
            return json.loads(m.group(0))
        raise RuntimeError(f"Model did not return valid JSON:\n{text}")

def friendly_message(json_assessment: dict) -> str:
    """Форматируем пациенту/врачу через тот же Responses API."""
    content = json.dumps(json_assessment, ensure_ascii=False)
    prompt = (
        "Convert the following strict JSON clinical assessment into:\n"
        "1) A friendly message for the patient (short, plain language).\n"
        "2) A concise clinician note (bullet points).\n\n"
        f"JSON:\n```json\n{content}\n```"
    )
    res = _client.responses.create(
        model=config.MODEL_FRIENDLY,  # теперь это gpt-5
        input=[
            {"role": "system", "content": SYSTEM_FRIENDLY},
            {"role": "user", "content": prompt},
        ],
        timeout=30,
    )
    return res.output_text
