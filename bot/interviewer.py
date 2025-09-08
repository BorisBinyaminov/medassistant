# bot/interviewer.py
from __future__ import annotations
from typing import List, Dict, Any
import json, re, logging

from bot import config
from .reviewer import _client  # OpenAI-клиент

log = logging.getLogger("interviewer")

SYSTEM_INTERVIEW = (
    "You are a friendly physician-assistant. Your goals: collect focused medical history, explain simply, "
    "and surface RED FLAGS. Be concise and proceed step-by-step.\n"
    "Always reply in the user's language for both 'ask' and 'explain'.\n"
    "Return STRICT JSON only (no markdown) with keys: "
    "{\"ask\": str, \"explain\": str, \"summary\": str, \"red_flags\": [str], \"urgent\": bool}.\n"
    "\n"
    "Core rules:\n"
    "- ALWAYS include the patient's own phrases in double quotes inside 'summary' "
    "(symptoms, timing, severity 0-10, triggers/relief, associated features, negatives if stated). Do not invent facts.\n"
    "- Keep 'ask' to ONE short question that moves triage forward, in the user's language.\n"
    "- Keep 'explain' to 1–2 short sentences (≤60 words), in the user's language. "
    "It may clarify why you ask this, but MUST NOT give diagnosis or treatment advice.\n"
    "- Only set ask=\"__DONE__\" AFTER you have these captured (quoted if possible): "
    "onset/timing, location, character, severity (0-10), triggers/relief, associated symptoms, key negatives, "
    "and any clinically relevant demographics.\n"
    "\n"
    "DEMOGRAPHICS POLICY (ask only if clinically relevant AND unknown):\n"
    "• Age: ask only when it changes triage/medication safety (child/toddler fever, headache, chest/abdominal/pelvic pain, UTI/pyelo, trauma). "
    "If age is stated, quote it in 'summary' (e.g., \"7 лет\" / \"55 years\"). Do not re-ask once captured.\n"
    "• Sex: ask only if it changes management (pelvic/urinary, breast/testicular issues). Include in 'summary' if known; do not re-ask.\n"
    "• Pregnancy: ask only when symptoms make it relevant (pelvic/abdominal pain, vaginal bleeding, dysuria, amenorrhea). "
    "Include quotes (e.g., \"8 недель беременна\" / \"not pregnant\") if stated; if unknown after one attempt, move on.\n"
    "\n"
    "LABS / REPORTS (optional; STRICT handling):\n"
    "- If the user mentions tests, ask them to paste key lines EXACTLY as written (e.g., "
    "\"CRP 126 mg/L (0–5) high\", \"Hb 8.9 g/dL (12–16) ↓\", \"SARS-CoV-2 ПЦР ПОЛОЖИТЕЛЬНЫЙ\"). "
    "Do NOT interpret — copy verbatim in quotes.\n"
    "- If multiple lab/report lines are provided across turns, maintain ONLY the LATEST and UNIQUE lines in 'summary':\n"
    "  • Prefer lines with explicit dates/times; if dates differ, keep the most recent only.\n"
    "  • For the same analyte/test with conflicting results (e.g., POSITIVE vs NEGATIVE), keep ONLY the most recent line.\n"
    "  • Deduplicate near-identical lines (normalize whitespace/case to check duplicates).\n"
    "  • Include at most 8 lab/report lines total; sort by recency (newest first).\n"
    "- If the date of a lab/report is unclear AND multiple versions exist, ask one short question to clarify which is the latest.\n"
    "- Mark nothing as facts beyond the quoted strings. Do not summarize labs; keep the exact text in quotes in 'summary'.\n"
    "\n"
    "Do NOT ask demographics when unlikely to affect decisions. Prefer targeted symptom questions first.\n"
    "'red_flags' are generic screening prompts to ASK ABOUT (not facts). Keep ≤4 and do NOT copy them into 'summary'.\n"
    "Set 'urgent' = true ONLY if the patient's OWN quoted words indicate immediate danger (e.g., \"упал в обморок\", "
    "\"боль в груди в покое\", \"черный стул\", \"сильная одышка\", \"рвота с кровью\"); otherwise false.\n"
)

def _messages_from_history(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    # history: [{"role":"user"/"assistant","content":"..."}]
    return [{"role": "system", "content": SYSTEM_INTERVIEW}, *history[-12:]]

_JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")

def _parse_json_relaxed(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        m = _JSON_BLOCK_RE.search(text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    raise json.JSONDecodeError("Unable to parse JSON from model output", text, 0)

def next_question(history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Возвращает словарь для верхнего хендлера:
      {
        "done": bool,                   # True, когда ask == "__DONE__"
        "question": str,                # следующий вопрос (или "" если done)
        "reason": str,                  # краткое пояснение источника
        "explain": str,                 # пояснение для пользователя
        "summary": str,                 # накопленное краткое резюме с кавычками
        "red_flags": List[str],         # до 4 скрининговых пунктов
        "urgent": bool                  # оценка срочности по словам пользователя
      }

    При сетевых/401 и др. серьёзных ошибках — жёстко завершаем:
      {"done": True, "question": "", "reason": "llm-error: ...", ...}
    """
    msgs = _messages_from_history(history)

    try:
        res = _client.responses.create(
            model=config.MODEL_REASONING,
            input=msgs,
            temperature=0.1,
            response_format={"type": "json"},   # требуем JSON на уровне API
        )
        text = res.output_text or ""
        log.debug("interviewer raw response: %s", text)

        data = _parse_json_relaxed(text)

        ask = (data.get("ask") or "").strip()
        explain = (data.get("explain") or "").strip()
        summary = (data.get("summary") or "").strip()
        red_flags = list(data.get("red_flags") or [])
        urgent = bool(data.get("urgent", False))

        done = (ask == "__DONE__")
        question = "" if done else ask

        # базовая валидация: если не done и вопрос пустой — подстрахуемся
        if not done and not question:
            question = "Что беспокоит больше всего прямо сейчас?"
            explain = explain or "Это поможет понять приоритет симптомов."
            src = "fallback: empty-ask"
        else:
            src = "model"

        return {
            "done": done,
            "question": question,
            "reason": src,
            "explain": explain,
            "summary": summary,
            "red_flags": red_flags[:4],
            "urgent": urgent,
        }

    except Exception as e:
        log.exception("interviewer failed: %s", e)
        # окончание сценария — верхний слой должен показать сервисное сообщение
        return {
            "done": True,
            "question": "",
            "reason": f"llm-error: {e}",
            "explain": "",
            "summary": "",
            "red_flags": [],
            "urgent": False,
        }
