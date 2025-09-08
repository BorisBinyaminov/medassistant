# bot/main.py
from __future__ import annotations
import asyncio
from pathlib import Path
from typing import Dict, List

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from html import escape
import json

from bot import config
from .utils import new_case_id, now_iso, normalize_text, sha256_of
from .ocr import ocr_image, parse_pdf
from .lab_extract import extract_panels
from .evidence_io import Evidence, append_evidence, load_evidence
from .handoff import quoted_evidence, package_outputs
from .reviewer import analyze_case, friendly_message
from .interviewer import next_question  # новый динамический интервьюер

# ---------- BOT ----------
bot = Bot(
    token=config.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher(storage=MemoryStorage())

# ---------- FSM ----------
class Intake(StatesGroup):
    dynamic = State()
    awaiting_file = State()
    awaiting_text = State()

# user_id -> текущий case_id
CURRENT_CASE: Dict[int, str] = {}

def case_for(user_id: int) -> str:
    if user_id not in CURRENT_CASE:
        CURRENT_CASE[user_id] = new_case_id()
    return CURRENT_CASE[user_id]

# ---------- Handlers ----------
@dp.message(CommandStart())
async def on_start(m: Message):
    await m.answer(
        "Привет! Начнём новый случай — /new\n\n"
        "<b>Команды:</b>\n"
        "• /new — начать новое дело (динамический опрос)\n"
        "• /add_text — добавить произвольный текст в текущее дело\n"
        "• /add_file — добавить файл (PDF/JPG/PNG) в текущее дело\n"
        "• /review &lt;case_id&gt; — клиническое резюме\n"
    )

@dp.message(Command("new"))
async def on_new(m: Message, state: FSMContext):
    user_id = m.from_user.id
    CURRENT_CASE[user_id] = new_case_id()
    await state.set_state(Intake.dynamic)
    await state.update_data(history=[], turns=0)
    await m.answer(
        f"🆕 Новое дело: <code>{CURRENT_CASE[user_id]}</code>\n"
        "Коротко опишите главную жалобу (одно предложение)."
    )

@dp.message(Intake.dynamic, F.content_type == ContentType.TEXT)
async def on_dynamic_step(m: Message, state: FSMContext):
    user_id = m.from_user.id
    case_id = case_for(user_id)
    text = normalize_text(m.text or "")

    # 1) сохраняем ответ в evidence
    ev = Evidence(
        case_id=case_id,
        user_id=user_id,
        role="patient_text",
        fragment=text,
        source={"type": "intake_dynamic", "message_id": m.message_id},
        created_at=now_iso(),
    )
    append_evidence([ev])

    # 2) поддерживаем историю для LLM
    data = await state.get_data()
    history: List[dict] = data.get("history", [])
    history.append({"role": "user", "content": text})
    turns = int(data.get("turns", 0)) + 1

    # 3) спрашиваем следующий шаг у модели
    resp = next_question(history)

    # 3a) если это LLM-ошибка — прекращаем сценарий
    if str(resp.get("reason", "")).startswith("llm-error"):
        await state.clear()
        await m.answer("⚠️ Техническая проблема при обращении к модели. Попробуйте ещё раз позже.")
        return

    done = bool(resp.get("done"))
    question = (resp.get("question") or "").strip()
    explain = (resp.get("explain") or "").strip()
    summary = (resp.get("summary") or "").strip()
    red_flags = list(resp.get("red_flags") or [])
    urgent = bool(resp.get("urgent", False))

    # 4) если закончили (или достигли лимита шагов) — показать итог
    if done or turns >= 12:
        await state.clear()

        parts = ["<b>Итог кратко</b>", summary or "—"]
        if red_flags:
            parts.append("<b>Что важно уточнить/отсечь (скрининг):</b>")
            for rf in red_flags[:4]:
                parts.append(f"• {escape(rf)}")
        if urgent:
            parts.append("❗️ По описанию это может быть срочно. Если состояние ухудшается — обратитесь за неотложной помощью.")

        parts.append(
            f"\nДело: <code>{case_id}</code>\n"
            "Можно прикрепить анализы через /add_file или добавить текст через /add_text.\n"
            f"Готовы к выводу? /review {case_id}"
        )
        await m.answer("\n".join(parts))
        return

    # 5) обычный шаг — короткое пояснение + следующий вопрос
    if explain:
        await m.answer(f"<i>{escape(explain)}</i>")
    if not question:
        question = "Что беспокоит больше всего прямо сейчас?"
    await m.answer(question)

    # 6) добавляем реплику ассистента в историю и сохраняем state
    history.append({"role": "assistant", "content": question})
    await state.update_data(history=history, turns=turns)

@dp.message(Command("add_text"))
async def on_add_text(m: Message, state: FSMContext):
    user_id = m.from_user.id
    cid = case_for(user_id)
    await state.set_state(Intake.awaiting_text)
    await m.answer(f"✍️ Пришлите текст одним сообщением. Дело: <code>{cid}</code>")

@dp.message(Intake.awaiting_text, F.content_type == ContentType.TEXT)
async def on_add_text_payload(m: Message, state: FSMContext):
    user_id = m.from_user.id
    case_id = case_for(user_id)
    text = normalize_text(m.text or "")
    ev = Evidence(
        case_id=case_id,
        user_id=user_id,
        role="patient_text",
        fragment=text,
        source={"type": "add_text", "message_id": m.message_id},
        created_at=now_iso(),
    )
    append_evidence([ev])
    await state.clear()
    await m.answer(f"📝 Текст добавлен к делу <code>{case_id}</code>.")

@dp.message(Command("add_file"))
async def on_add_file(m: Message, state: FSMContext):
    user_id = m.from_user.id
    cid = case_for(user_id)
    await state.set_state(Intake.awaiting_file)
    await m.answer(f"📎 Пришлите файл (PDF/JPG/PNG). Дело: <code>{cid}</code>")

@dp.message(Intake.awaiting_file, F.content_type.in_({ContentType.DOCUMENT, ContentType.PHOTO}))
async def on_file_payload(m: Message, state: FSMContext):
    user_id = m.from_user.id
    case_id = case_for(user_id)

    # скачать файл
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
    meta = {"type": "upload", "path": str(dest), "sha256": sha256_of(raw)}

    fragments = []
    if dest.suffix.lower() == ".pdf":
        full, per_page = parse_pdf(dest)
        fragments.append(("ocr", full, {**meta}))
        for page_idx, page_text in per_page:
            fragments.append(("ocr", page_text, {**meta, "page": page_idx}))
    else:
        text = ocr_image(dest)
        fragments.append(("ocr", text, meta))

    # Примитивная выжимка лабораторных панелей (regex)
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
            source=meta2,
            created_at=now_iso(),
        )
        for role, frag, meta2 in fragments
    ]
    append_evidence(evs)

    await state.clear()
    await m.answer(
        f"📄 Файл добавлен к делу <code>{case_id}</code>. "
        f"Можно /add_file ещё или /review {case_id}."
    )

@dp.message(Command("review"))
async def on_review(m: Message):
    parts = (m.text or "").split()
    if len(parts) < 2:
        cid = CURRENT_CASE.get(m.from_user.id)
        if not cid:
            await m.answer("Укажите: /review <case_id> или начните с /new.")
            return
        case_id = cid
    else:
        case_id = parts[1].strip()

    user_id = m.from_user.id
    evs = load_evidence(case_id, user_id)
    if not evs:
        await m.answer("Не нашёл доказательств для этого дела. Сначала /new и ответы на вопросы.")
        return

    quotes = quoted_evidence(evs)
    await m.answer("🧠 Анализирую кейс…")

    try:
        assessment = analyze_case(case_id, quotes)  # STRICT JSON от модели
        friendly = friendly_message(assessment)     # дружелюбный текст
    except Exception as e:
        await m.answer(f"❌ Ошибка при обращении к модели:\n<code>{escape(str(e))}</code>")
        return

    pkg = package_outputs(case_id, assessment, friendly)

    json_str = json.dumps(pkg["clinical_json"], ensure_ascii=False, indent=2)
    json_html = escape(json_str)

    await m.answer(
        "<b>Клиническое резюме</b>\n"
        + friendly
        + f"\n\n<code>JSON:</code>\n<pre language=\"json\">{json_html}</pre>"
    )

# Фоллбек: вне интейка — подсказка
@dp.message(F.content_type == ContentType.TEXT)
async def on_free_text(m: Message):
    await m.answer(
        "Я сейчас собираю данные только через сценарий. Нажмите /new и отвечайте на вопросы.\n"
        "Для вложений используйте /add_file, для доп. текста — /add_text."
    )

def run() -> None:
    import logging
    level = logging.DEBUG if config.DEBUG else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    run()
