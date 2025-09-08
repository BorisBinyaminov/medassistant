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