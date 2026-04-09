FROM python:3.11-slim

LABEL org.opencontainers.image.title="aerotrack-api"
LABEL org.opencontainers.image.description="FastAPI inference service for aerial object detection and tracking."
LABEL org.opencontainers.image.source="https://github.com/joshleh/aerotrack"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["sh", "-c", "python scripts/bootstrap_runtime.py && uvicorn api.main:app --host ${API_HOST:-0.0.0.0} --port ${PORT:-${API_PORT:-8000}}"]
