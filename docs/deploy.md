# Deployment Guide

This guide covers the most practical ways to run `aerotrack` beyond local development.

## Recommended no-cost path

If the goal is a public challenge URL without committing to monthly spend, the best current fit is a single free Render web service for the API demo.

Why this is the best default:

- Render officially supports `free` web-service instances in `render.yaml`
- Docker deployments are supported directly from your repository
- the free web tier is enough for a low-traffic portfolio demo
- the tradeoff is that free services can spin down when idle, so it is best for demos, judging, and portfolio review rather than production uptime

Recommended public architecture:

- deploy the FastAPI browser demo only
- make MLflow optional for the public URL
- fetch the chosen checkpoint at startup using `AEROTRACK_MODEL_URL`
- keep uploads short and demo-oriented

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

Current recommendation:

- choose Render first for the public demo, because it has an official `free` web-service plan and native Blueprint support

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
AEROTRACK_MODEL_PATH=/app/models/aerotrack-detector.pt
AEROTRACK_MODEL_URL=https://example.com/path/to/model.pt
AEROTRACK_DEVICE=cpu
AEROTRACK_CONFIDENCE=0.25
AEROTRACK_IOU=0.45
AEROTRACK_OUTPUT_DIR=/app/outputs
MLFLOW_UI_URL=
```

`AEROTRACK_MODEL_URL` is the key to a free-tier deployment with no persistent disk. On startup, the container downloads the model into `AEROTRACK_MODEL_PATH` if it is not already present.

For MLflow:

```dotenv
MLFLOW_BACKEND_STORE_URI=sqlite:////mlflow/mlflow.db
MLFLOW_ARTIFACT_ROOT=/mlflow/artifacts
```

## Render deployment

The repository includes [render.yaml](/Users/joshu/aerotrack/render.yaml), which defines a free Render web service for the demo app.

The current repo is also set up to bundle the stronger RTX 4070 Ti checkpoint directly under `models/` so the public deployment can work immediately without requiring an external model host. Later, you can still switch to `AEROTRACK_MODEL_URL` if you want to ship a newer model without committing it into the repo.

Suggested flow:

1. Push the latest repo state to GitHub.
2. In Render, create a new Blueprint from the repo.
3. Keep the service on the `free` plan.
4. Set `AEROTRACK_MODEL_URL` to a public direct-download URL for your chosen checkpoint.
5. Optionally set `MLFLOW_UI_URL` if you want the homepage to link to a hosted MLflow instance.
6. Deploy and verify `/health`, `/metadata`, `/detect`, and `/track`.

Where to host the model file cheaply:

- a GitHub Release asset
- a Hugging Face model repository file
- any public direct-download object URL you control

### Why not deploy MLflow on the free path

For the challenge URL, the browser demo matters more than hosting the experiment tracker publicly.

Keeping MLflow out of the first public deployment:

- reduces memory pressure
- avoids managing a persistent backend database
- lowers the risk of free-tier instability

You can still show MLflow locally in recordings and screenshots.

## Public demo advice

If you want a cheap live demo:

1. Deploy the API container first
2. Start with CPU inference
3. Use a pre-exported trained weight file via `AEROTRACK_MODEL_URL`
4. Keep request sizes small for demo clips
5. Treat MLflow as optional for the public demo if operating two services is too much friction

### API start command

The container already starts with:

```bash
uvicorn api.main:app --host 0.0.0.0 --port ${API_PORT}
```

- expose `/health` for quick verification
- use the browser demo at `/` as the primary submission URL
- keep one known-good image and one short clip ready for judging
- refresh the deployed checkpoint once the stronger GPU-trained model is ready

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
