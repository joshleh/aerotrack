# AeroTrack Session Handoff

Date: 2026-04-09

This note captures the important outcomes from the build/deploy session so the project can be resumed quickly on another machine.

## Current repo state

- Branch: `main`
- Working tree: clean
- Latest pushed commit: `fb0e170` - `feat: bundle validation checkpoint for render demo`

Recent key commits:

- `fb0e170` - bundle validation checkpoint for Render demo
- `2c64f6d` - clarify demo checkpoint status
- `02bec75` - prepare aerotrack for public demo deployment
- `20b7251` - add browser demo for aerotrack
- `da37454` - add demo capture guide
- `0eb36bb` - add operator metadata and runbook

## What is working

- FastAPI API for `/detect` and `/track`
- Browser demo at `/`
- Runtime metadata at `/metadata`
- MLflow local setup
- Docker local bring-up
- VisDrone dataset download + YOLO conversion script
- Training pipeline validation run
- Tracking smoke test
- API tests
- Render deployment configuration

## Current demo model

The currently deployed/demo-ready checkpoint is:

- `models/aerotrack-detector-validation.pt`

This is a validated interim checkpoint from a successful local CPU run, not the final GPU-trained showcase model.

## Local URLs

- App: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`
- Metadata: `http://localhost:8000/metadata`
- MLflow: `http://localhost:5001`

## Training status

The pipeline has already completed a successful validation run with reduced settings:

- epochs: `1`
- imgsz: `640`
- batch: `2`

The resulting metrics were enough to prove the system works end to end, but they are not intended to be the final public model metrics.

The original heavier CPU configuration was not viable on the MacBook and ran into resource pressure.

## Recommended next step on the gaming PC

Use the gaming computer with the `4070 Ti` for the stronger training run.

Suggested flow:

1. Clone the repo.
2. Set up Python `3.11`.
3. Install CUDA-enabled PyTorch and the rest of the project dependencies.
4. Reuse the prepared VisDrone dataset flow if needed.
5. Run a fuller training configuration and export the improved checkpoint.
6. Replace the current validation checkpoint in deployment once the stronger model is ready.

Likely training command shape:

```bash
python -m src.train \
  --data data/visdrone/VisDrone.yaml \
  --epochs 50 \
  --imgsz 1024 \
  --batch 8 \
  --mlflow-tracking-uri http://localhost:5001
```

Tune `batch` based on actual VRAM headroom.

## Deployment status

The repo is prepared for Render deployment with:

- `render.yaml`
- startup bootstrap script
- bundled validation checkpoint

For the current public demo, the deployed app should show a subtle note that a stronger GPU-trained model is the next planned upgrade.

## Notes on model hosting later

For the final public showcase, the cleaner long-term path is:

1. train the better checkpoint on the gaming PC
2. upload it as a GitHub Release asset or another public model host
3. point deployment at that stronger artifact

The current bundled checkpoint is mainly for convenience and fast interim deployment.
