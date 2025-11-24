# syntax=docker/dockerfile:1.7

FROM python:3.11-slim-bookworm AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/root/.cache/uv \
    UV_LINK_MODE=copy \
    NOUGAT_CHECKPOINT=/root/.cache/torch/hub/nougat-0.1.0-base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        poppler-utils \
        tesseract-ocr \
        ghostscript \
        libxml2 \
        libxslt1.1 \
        libgl1 \
        libglib2.0-0 \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instalação do UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY pdfs-reais ./pdfs-reais

RUN uv sync --frozen --no-dev

RUN uv run python - <<'PY'
from nougat.utils.checkpoint import get_checkpoint
get_checkpoint(model_tag="0.1.0-base")
PY

RUN uv pip install --upgrade --force-reinstall "albumentations>=1.3,<1.4"

COPY docs ./docs

CMD ["uv", "run", "pdf-extractor", "--help"]

