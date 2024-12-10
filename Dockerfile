
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim


WORKDIR /app


RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN uv pip install -r requirements.txt

COPY . .

RUN mkdir -p uploads reports cached_data nltk_data \
    && chmod 755 uploads reports cached_data nltk_data

RUN python setup.py

ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

EXPOSE 5001

CMD ["./run.sh"]