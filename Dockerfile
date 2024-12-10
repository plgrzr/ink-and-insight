FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN uv pip install -r requirements.txt --system

COPY . .

RUN mkdir -p uploads reports cached_data nltk_data \
    && chmod 755 uploads reports cached_data nltk_data

RUN python setup.py

ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

EXPOSE 5001

CMD ["./run.sh"]