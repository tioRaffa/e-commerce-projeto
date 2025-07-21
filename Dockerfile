FROM python:3.11-slim-bookworm
LABEL maintainer="rafaelmuniz200@gmail.com"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/ven/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dit -r requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

RUN groupadd --system --gid 1001 appuser && \
    useradd --system --uid 1001 --gid appuser --shell /bin/sh --no-create-home appuser && \
    mkdir -p /app/scripts && \
    chmod -R +x /app/scripts

COPY . .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/scripts/commands.sh"]