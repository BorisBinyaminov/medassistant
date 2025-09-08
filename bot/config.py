# bot/config.py
from pathlib import Path
import os

# Опционально: автозагрузка .env (если хочешь)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=".env")
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
DB_PATH = ARTIFACTS_DIR / "db" / "evidence.jsonl"
COMPARE_DIR = ARTIFACTS_DIR / "compare"

# === Обязательные переменные ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # must be set
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")          # must be set

# === Опциональные ===
#OPENAI_ORG = os.environ.get("OPENAI_ORG")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL_REASONING = os.environ.get("MODEL_REASONING", "gpt-5")
MODEL_FRIENDLY  = os.environ.get("MODEL_FRIENDLY", "gpt-5-chat")
DEBUG = os.environ.get("DEBUG", "false").lower() in ("1", "true", "yes")

# создать директории
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
(DB_PATH.parent).mkdir(parents=True, exist_ok=True)
COMPARE_DIR.mkdir(parents=True, exist_ok=True)

# маленькая проверка на обязательные
_missing = [k for k,v in {
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "OPENAI_API_KEY": OPENAI_API_KEY,
}.items() if not v]
if _missing:
    raise RuntimeError(f"Missing required env vars: {', '.join(_missing)} (check your .env)")
