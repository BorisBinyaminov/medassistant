FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Системные зависимости (OCR/Poppler — если нужны)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr libtesseract-dev poppler-utils \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) сначала только зависимости — кэшируется
COPY bot/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
 && pip install --prefer-binary -r /tmp/requirements.txt

# 2) затем код — быстрые слои
COPY bot/ /app/bot/

CMD ["python", "-m", "bot.main"]
