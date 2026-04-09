# Demo Guide

This guide is for presenting `aerotrack` in an interview, portfolio review, or challenge submission without wandering through the repo live.

## The 30-second pitch

`aerotrack` is an end-to-end aerial perception pipeline for multi-object detection and tracking on drone imagery. It fine-tunes YOLOv8 on VisDrone, assigns persistent track IDs with ByteTrack, serves inference with FastAPI, tracks experiments in MLflow, and runs in Docker.

## What to emphasize

- This is not just model training; it is a full perception-service workflow
- The dataset is aerial and domain-aligned rather than generic
- Tracking is not just frame-by-frame detection; it includes persistent identity assignment
- MLflow makes runs reproducible and inspectable
- Docker packaging means another engineer can actually run it

## Suggested 3-minute demo flow

1. Start with the architecture diagram in [README.md](/Users/joshu/aerotrack/README.md).
2. Show the running services with `docker-compose ps`.
3. Hit `GET /health` to confirm the API is live.
4. Run `POST /detect` on a VisDrone frame and show the JSON detections.
5. Run `POST /track` on a short clip and point out persistent `track_id` values.
6. Open MLflow on `localhost:5001` and show experiment runs, artifacts, and model outputs.
7. Close by explaining that the same repo contains training, tracking, API serving, and containerized deployment.

## Suggested talking points

### Detection

- YOLOv8m is the default detector
- VisDrone gives aerial-domain training data with dense scenes and small objects
- The training pipeline logs metrics and artifacts to MLflow rather than leaving them in a local notebook

### Tracking

- The tracker layer converts detections into persistent identities across frames
- ByteTrack brings in Kalman filter-based multi-object tracking behavior, which is directly relevant to classical state estimation and perception pipelines

### MLOps

- Environment-driven config prevents hardcoded credentials and machine-specific paths
- MLflow stores experiment metadata, metrics, and artifacts
- Docker Compose packages the API and tracking server together for local reproducibility

## If a recruiter asks "why this matters"

This project demonstrates the exact blend of skills many autonomy and perception teams care about:

- modern CV model integration
- classical tracking ideas in a practical system
- production-style interfaces and packaging
- reproducibility and experiment management

## If the live demo is slow

Use this fallback structure:

1. Show `GET /health`
2. Show a saved `/detect` response
3. Show a saved `/track` response with stable IDs
4. Show the MLflow UI
5. Explain that full training on CPU is intentionally validated with reduced settings locally, while larger runs are intended for more capable hardware

## Demo assets worth capturing

- Terminal output from `docker-compose up --build`
- `GET /health` response
- One `/detect` JSON response
- One `/track` JSON response
- MLflow experiment page
- Annotated tracking clip output from `/app/outputs`

