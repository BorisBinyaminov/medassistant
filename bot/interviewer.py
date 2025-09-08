# bot/interviewer.py
from __future__ import annotations
from typing import List, Dict, Any
import json, re, logging

from bot import config
from .reviewer import _client  # это уже OpenAI-клиент с httpx

log = logging.getLogger("interviewer")

SYSTEM_INTERVIEW = (
    "You are MedAssistant, a clinical interviewer. "
    "Ask ONE short follow-up question at a time. "
    "Stop when enough info for initial triage. "
    "Return STRICT JSON only: {\"done\": boolean, \"question\": string, \"reason\": string}. "
    "Write the question in Russian."
)

def _messages_from_history(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_INTERVIEW}, *history]

def _parse_json_strict(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception as e:
        m = re.search(r"\{[\s\S]*\}$", text)
        if m:
            return json.loads(m.group(0))
        raise e

def next_question(history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Возвращает {'done': bool, 'question': str, 'reason': str}
    Если парсинг не удался → кидаем исключение, чтобы хендлер сам завершил опрос.
    """
    msgs = _messages_from_history(history)
    try:
        res = _client.responses.create(
            model=config.MODEL_REASONING,
            input=msgs,
            temperature=0.1,
        )
        text = res.output_text or ""
        log.debug("interviewer raw response: %s", text)

        parsed = _parse_json_strict(text)
        done = bool(parsed.get("done", False))
        question = (parsed.get("question") or "").strip()
        reason = (parsed.get("reason") or "model").strip()
        if not question and not done:
            raise ValueError("empty-question-from-model")
        return {"done": done, "question": question, "reason": reason}

    except Exception as e:
        # Логируем и пробрасываем ошибку дальше
        log.exception("interviewer parsing failed: %s", e)
        raise RuntimeError("model_failed") from e

