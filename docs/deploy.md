# Deployment Guide

This guide covers the most practical ways to run `aerotrack` beyond local development.

## Deployment modes

### 1. Local Docker Compose

Best for:

- development
- smoke testing
- demo recording
- MLflow experiment review on a single machine

Command:

```bash
docker-compose up --build
```

Services:

- FastAPI API on `localhost:8000`
- MLflow UI on `localhost:5001`

### 2. Single-service API deployment

Best for:

- live challenge demos
- simple hosted inference endpoints
- lightweight portfolio deployments

In this mode, deploy only the API container and point it at:

- a preloaded model path
- an external MLflow tracking server, if you want experiment logging

Good fits:

- Render web service
- Railway service
- Fly.io app

### 3. Split deployment

Best for:

- more serious demos
- shared experiment tracking
- team usage

Recommended split:

- API service deployed separately
- MLflow deployed as its own service
- artifact storage moved to persistent disk or object storage
- model artifacts/versioning managed outside the API filesystem

## Minimum environment variables

For the API service:

```dotenv
API_HOST=0.0.0.0
API_PORT=8000
AEROTRACK_MODEL_PATH=yolov8m.pt
AEROTRACK_DEVICE=cpu
AEROTRACK_CONFIDENCE=0.25
AEROTRACK_IOU=0.45
AEROTRACK_OUTPUT_DIR=/app/outputs
MLFLOW_TRACKING_URI=http://mlflow:5000
```

For MLflow:

```dotenv
MLFLOW_BACKEND_STORE_URI=sqlite:////mlflow/mlflow.db
MLFLOW_ARTIFACT_ROOT=/mlflow/artifacts
```

## Render / Railway style deployment notes

If you want a cheap live demo:

1. Deploy the API container first
2. Start with CPU inference
3. Use a base YOLO checkpoint or a pre-exported trained weight file
4. Keep request sizes small for demo clips
5. Treat MLflow as optional for the public demo if operating two services is too much friction

### API start command

The container already starts with:

```bash
uvicorn api.main:app --host 0.0.0.0 --port ${API_PORT}
```

### Public demo advice

- expose `/health` for quick verification
- pre-generate one or two known-good demo clips
- keep model weights available in the container image or attached volume
- avoid depending on first-request model downloads in production demos

## Production-minded follow-ups

If this repo were extended into a more operational system, the next infrastructure upgrades would be:

- move MLflow backend from SQLite to Postgres
- move artifacts to object storage
- bake model weights into an artifact bundle or registry flow
- add structured request logging
- add request size limits and auth in front of the API
- add a background job path for long-running video tracking

## Operational checklist

Before calling a deployment "demo-ready":

1. `GET /health` returns `200`
2. `POST /detect` works on a known sample frame
3. `POST /track` works on a known short clip
4. MLflow UI is reachable if enabled
5. Model weights are present and do not require surprise downloads during the demo

