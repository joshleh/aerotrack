# Demo Capture Guide

This guide is the exact order to use for a clean `aerotrack` demo capture using the stronger RTX 4070 Ti checkpoint produced by the training pipeline.

## Goal

Show that:

1. the system starts cleanly
2. the API is live
3. detection works
4. tracking works
5. MLflow contains a completed training run
6. the API is serving the stronger GPU-trained checkpoint rather than the base model

## Pre-demo setup

Confirm the API is pointed at the stronger GPU-trained checkpoint:

```bash
curl http://localhost:8000/metadata
```

You want `/metadata` to show:

```text
/app/models/aerotrack-detector-demo-v2.pt

The browser runtime panel should show:

```text
AeroTrack Detector v2
```
```

## Recommended capture sequence

### 1. Stack health

Capture:

```bash
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8000/metadata
```

Good talking point:

- "The API is serving a stronger checkpoint produced by the training pipeline, not just the default base model."

### 2. Single-frame detection

Use a known VisDrone image:

```bash
curl -X POST "http://localhost:8000/detect" \
  -H "accept: application/json" \
  -F "file=@data/raw/VisDrone2019-DET-val/images/0000271_01401_d_0000380.jpg"
```

Capture:

- terminal response
- a few high-confidence detections in the JSON

### 3. Tracking

Generate a short smoke-test clip if needed:

```bash
docker-compose exec api python scripts/make_smoke_clip.py \
  --image data/raw/VisDrone2019-DET-val/images/0000271_01401_d_0000380.jpg \
  --output outputs/demo_smoke.mp4
```

Then run tracking:

```bash
curl -X POST "http://localhost:8000/track" \
  -H "accept: application/json" \
  -F "file=@outputs/demo_smoke.mp4"
```

Capture:

- frame-wise `track_id` output
- the generated annotated video path

### 4. MLflow

Open:

```text
http://localhost:5001
```

Capture:

- the completed stronger GPU training run and its metrics
- the logged metrics
- the plots / artifact list

Good talking point:

- "I validated the pipeline locally first, then trained the stronger showcase checkpoint on an RTX 4070 Ti."

## Suggested narration

Use something like:

> AeroTrack is an end-to-end aerial perception pipeline for drone footage. I trained a VisDrone detector, exposed it through FastAPI for single-frame and clip-level inference, tracked experiments in MLflow, and packaged the workflow with Docker. This demo is using the stronger RTX 4070 Ti-trained checkpoint from that pipeline.

## Demo assets to save

- terminal screenshot of `docker-compose ps`
- `/health` response
- `/metadata` response
- `/detect` response
- `/track` response
- annotated clip output
- MLflow run page
