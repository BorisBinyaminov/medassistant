# bot/interviewer.py
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Tuple

from openai import OpenAI

from . import config
from .prompts_v3 import INTAKE_SYSTEM_V3

log = logging.getLogger("interviewer")

# --- OpenAI client (org заголовок передаём только если задан) ---
_client = OpenAI(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_BASE_URL,
    organization=(config.OPENAI_ORG or None),
)


def _messages_from_history(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    История → формат для Responses API: [{"role": "...", "content": "..."}]
    Добавляем системный промпт, требуем STRICT JSON.
    """
    sys = (
        INTAKE_SYSTEM_V3
        + "\n\nВАЖНО: отвечай ТОЛЬКО строгим JSON-объектом без каких-либо префиксов/суффиксов."
    )
    msgs: List[Dict[str, str]] = [{"role": "system", "content": sys}]
    for turn in history:
        role = turn.get("role") or "user"
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        msgs.append({"role": role, "content": content})
    return msgs


# ---------------- JSON parsing helpers ----------------

_JSON_FENCE_RE = re.compile(
    r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE
)

def _scan_brace_object(s: str) -> str | None:
    """
    Находит первый валидный JSON-объект по балансу фигурных скобок.
    Возвращает подстроку "{ ... }" или None.
    """
    start = s.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return s[start : i + 1]
    return None


def _parse_json_strict(text: str) -> Dict[str, Any]:
    """
    Пытается распарсить строгий JSON-объект из строки.
    1) прямая попытка json.loads
    2) блоки в ```json ... ```
    3) сканер по балансу скобок
    """
    t = (text or "").strip()

    # простейший случай
    try:
        obj = json.loads(t)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # поиск в блоке ```json ... ```
    m = _JSON_FENCE_RE.search(t)
    if m:
        candidate = m.group(1)
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass

    # скан по балансу скобок
    candidate = _scan_brace_object(t)
    if candidate:
        obj = json.loads(candidate)  # пусть ошибка вылетит наверх
        if isinstance(obj, dict):
            return obj

    raise ValueError("no-json-object-found")


# ---------------- Public API ----------------

def next_question(history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Возвращает dict с ключами:
      question, explain, summary, red_flags, urgent, done, reason
    Если происходит ошибка LLM/парсинга — возвращает:
      {"done": True, "reason": "llm-error: <...>"}
    """
    msgs = _messages_from_history(history)

    try:
        res = _client.responses.create(
            model=config.MODEL_REASONING,
            input=msgs,
            temperature=0.1,
        )
        text = getattr(res, "output_text", None) or ""
        log.debug("interviewer raw response: %s", text)

        parsed_raw = _parse_json_strict(text)
        # нормализуем ключи к нижнему регистру для устойчивости
        parsed = { (k or "").lower(): v for k, v in parsed_raw.items() }

        ask = (parsed.get("ask") or "").strip()
        explain = (parsed.get("explain") or "").strip()
        summary = (parsed.get("summary") or "").strip()
        red_flags = list(parsed.get("red_flags") or [])
        urgent = bool(parsed.get("urgent", False))
        done = bool(parsed.get("done", False)) or (ask == "__DONE__")

        if not done and not ask:
            raise ValueError("empty-ask-from-model")

        return {
            "done": done,
            "question": ("" if ask == "__DONE__" else ask),
            "explain": explain,
            "summary": summary,
            "red_flags": red_flags,
            "urgent": urgent,
            "reason": parsed.get("reason") or "model",
        }

    except Exception as e:
        log.exception("interviewer failed: %s", e)
        # Cигнализируем хендлеру остановить интервью и сообщить о проблеме
        return {"done": True, "reason": f"llm-error: {e}"}
