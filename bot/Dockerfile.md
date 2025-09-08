# bot/Dockerfile
FROM python:3.11-slim

# Системные зависимости для OCR/PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-rus poppler-utils libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Работаем в /app
WORKDIR /app

# Сначала зависимости — чтобы кэшировалось
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Потом код
COPY . /app

# Без буфера для логов
ENV PYTHONUNBUFFERED=1

# Точка входа (в compose можно перегрузить command:)
CMD ["python", "-m", "bot.main"]
