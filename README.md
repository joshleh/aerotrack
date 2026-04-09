# aerotrack

`aerotrack` is an end-to-end MLOps pipeline for multi-object detection and tracking on aerial drone footage. It is built to look and feel like a real perception-system project: public aerial data ingestion, YOLOv8 fine-tuning, Kalman filter-based tracking via ByteTrack, experiment tracking in MLflow, and a containerized FastAPI inference surface for detection and clip-level tracking.

This project is intentionally framed around Anduril-relevant capabilities:

- aerial perception on drone imagery
- persistent multi-object tracking
- real-time inference APIs
- reproducible model training and experiment tracking
- model packaging and deployment with Docker

## Why this project

Anduril-style perception work sits at the intersection of modern deep learning, classical tracking, and operational ML systems. `aerotrack` demonstrates all three:

- `YOLOv8` handles contemporary object detection
- `ByteTrack` provides persistent IDs across frames using a Kalman filter-based MOT pipeline
- `MLflow` captures metrics, artifacts, and model versions so experiments are not one-off notebook runs
- `FastAPI` exposes the system in a form another service or operator workflow could actually call

The result is a repo that is closer to a deployable perception service than a one-off computer vision demo.

## Core capabilities

- Fine-tune `yolov8m` on `VisDrone2019-DET`
- Track detections across frames with `ByteTrack`
- Serve `POST /detect` for single-frame inference
- Serve `POST /track` for clip-level tracking results
- Serve a browser-ready demo at `GET /`
- Log training metrics, plots, and model artifacts to MLflow
- Run the API and tracking server locally with `docker-compose`

## Stack

| Layer | Tooling |
| --- | --- |
| Detection | Ultralytics YOLOv8 |
| Tracking | Supervision ByteTrack |
| Inference API | FastAPI |
| Experiment tracking | MLflow |
| CV / DL runtime | OpenCV, PyTorch |
| Packaging | Docker, docker-compose |
| Dataset | VisDrone2019-DET |

## Why VisDrone

VisDrone is a strong fit for this project because it contains publicly available drone-captured imagery with dense annotations for pedestrians, cars, vans, buses, trucks, bicycles, and related classes. It is thematically aligned with low-altitude aerial surveillance, urban scene understanding, and persistent object monitoring, which makes it much more compelling here than a generic object detection benchmark.

## Architecture

```text
                    +-----------------------------+
                    |      VisDrone2019-DET       |
                    |  download -> convert YOLO   |
                    +-------------+---------------+
                                  |
                                  v
                    +-------------+---------------+
                    |         src/train.py        |
                    | YOLOv8m fine-tuning         |
                    | MLflow params + metrics     |
                    +-------------+---------------+
                                  |
                                  v
                    +-------------+---------------+
                    |        MLflow Server        |
                    | runs, plots, artifacts,     |
                    | model registry metadata     |
                    +-------------+---------------+
                                  |
               +------------------+------------------+
               |                                     |
               v                                     v
     +---------+----------+               +----------+----------+
     |   src/predict.py   |               |    src/track.py     |
     | single-frame det   |               | YOLO + ByteTrack    |
     +---------+----------+               +----------+----------+
               |                                     |
               +------------------+------------------+
                                  |
                                  v
                    +-------------+---------------+
                    |         FastAPI API         |
                    |    /detect and /track       |
                    +-----------------------------+
```

## Repository layout

```text
aerotrack/
├── api/
│   ├── main.py
│   ├── routes/
│   └── schemas.py
├── data/
│   └── README.md
├── mlflow/
│   └── mlflow.dockerfile
├── notebooks/
│   └── 01_eda.ipynb
├── scripts/
│   ├── download_visDrone.sh
│   └── make_smoke_clip.py
├── src/
│   ├── predict.py
│   ├── track.py
│   ├── train.py
│   └── utils.py
├── docs/
│   ├── demo.md
│   └── deploy.md
├── examples/
│   ├── detect_response.json
│   └── track_response.json
├── .dockerignore
├── .env.example
├── .env.production.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Quickstart

1. Clone the repository.

```bash
git clone <your-repo-url>
cd aerotrack
```

2. Create your local environment file.

```bash
cp .env.example .env
```

Recommended local values:

```dotenv
API_HOST=0.0.0.0
API_PORT=8000
AEROTRACK_MODEL_PATH=yolov8m.pt
AEROTRACK_DEVICE=cpu
AEROTRACK_CONFIDENCE=0.25
AEROTRACK_IOU=0.45
AEROTRACK_OUTPUT_DIR=/app/outputs
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_EXPERIMENT_NAME=aerotrack-yolov8
MLFLOW_MODEL_NAME=aerotrack-detector
MLFLOW_BACKEND_STORE_URI=sqlite:////mlflow/mlflow.db
MLFLOW_ARTIFACT_ROOT=/mlflow/artifacts
```

3. Download and prepare VisDrone.

```bash
chmod +x scripts/download_visDrone.sh
./scripts/download_visDrone.sh
```

4. Build and start the stack.

```bash
docker-compose up --build
```

5. Verify the API is live.

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Optional runtime metadata:

```bash
curl http://localhost:8000/metadata
```

Browser demo:

```text
http://localhost:8000/
```

## Dataset setup

The repository includes a reproducible VisDrone prep flow:

- [data/README.md](/Users/joshu/aerotrack/data/README.md) explains the official source and expected output structure
- [scripts/download_visDrone.sh](/Users/joshu/aerotrack/scripts/download_visDrone.sh) downloads the train / val / test-dev archives, extracts them, converts annotations into YOLO format, and generates `data/visdrone/VisDrone.yaml`

This means a fresh clone can move from raw data to training-ready layout with a single command.

## Inference API

### `POST /detect`

Single-frame inference via multipart upload:

```bash
curl -X POST "http://localhost:8000/detect" \
  -H "accept: application/json" \
  -F "file=@/absolute/path/to/frame.jpg"
```

Example response:

```json
{
  "detections": [
    {
      "bbox": [113.6, 87.2, 164.9, 141.0],
      "class_id": 3,
      "class_label": "car",
      "confidence": 0.9142
    }
  ]
}
```

### `POST /track`

Clip-level tracking via multipart upload:

```bash
curl -X POST "http://localhost:8000/track" \
  -H "accept: application/json" \
  -F "file=@/absolute/path/to/clip.mp4"
```

Example response:

```json
{
  "frames": [
    {
      "frame_index": 0,
      "objects": [
        {
          "track_id": 7,
          "bbox": [114.3, 87.0, 166.2, 140.8],
          "class_id": 3,
          "class_label": "car",
          "confidence": 0.91
        }
      ]
    }
  ],
  "annotated_video_path": "/app/outputs/clip_tracked.mp4",
  "metadata": {
    "source_filename": "clip.mp4"
  }
}
```

To generate a short repeat-frame smoke-test clip from a single image:

```bash
python scripts/make_smoke_clip.py \
  --image data/raw/VisDrone2019-DET-val/images/0000271_01401_d_0000380.jpg \
  --output outputs/smoke.mp4
```

If you are working from the Dockerized environment instead of a local Python environment, use:

```bash
docker-compose exec api python scripts/make_smoke_clip.py \
  --image data/raw/VisDrone2019-DET-val/images/0000271_01401_d_0000380.jpg \
  --output outputs/smoke.mp4
```

## Training and MLflow

Run training locally from the repo root:

```bash
python -m src.train \
  --data data/visdrone/VisDrone.yaml \
  --epochs 50 \
  --imgsz 1024 \
  --batch 8 \
  --lr 0.001 \
  --mlflow-tracking-uri "$MLFLOW_TRACKING_URI"
```

Run training from the Dockerized API service:

```bash
docker-compose exec api python -m src.train \
  --data data/visdrone/VisDrone.yaml \
  --epochs 1 \
  --imgsz 640 \
  --batch 2 \
  --mlflow-tracking-uri http://mlflow:5000
```

`src/train.py` logs:

- hyperparameters
- per-epoch loss curves
- `mAP50`
- `mAP50-95`
- Ultralytics plots and CSV outputs
- final model artifact

The default registry name is `aerotrack-detector`.

Open MLflow at [http://localhost:5001](http://localhost:5001) to inspect runs, compare metrics, and browse model registry entries.

## Local training note

The full default configuration in this repo is designed as a production-style starting point, not a promise that every laptop can train `yolov8m` efficiently on CPU. In local Docker testing, reduced settings such as `--epochs 1 --imgsz 640 --batch 2` are a safer validation path. For the full `imgsz=1024, batch=8` flow, a machine with more memory and ideally GPU acceleration is the better target.

## Demo checklist

If you are using this project in an interview, challenge, or portfolio setting, the most effective demo flow is:

1. Show `docker-compose up --build`
2. Hit `GET /health`
3. Run `POST /detect` on a VisDrone frame
4. Run `POST /track` on a short clip and show persistent IDs
5. Open MLflow and show the run history plus logged artifacts

That demonstrates modeling, tracking, API design, experiment management, and containerization in one pass.

For a tighter presentation outline, use [docs/demo.md](/Users/joshu/aerotrack/docs/demo.md).

## What makes this project credible

- It uses a real aerial dataset rather than generic COCO-only examples
- It combines deep detection with classical MOT logic
- It exposes a service boundary instead of stopping at notebook output
- It tracks experiments and artifacts in MLflow
- It is packaged so another engineer can run it with Docker

## Security and config hygiene

- No credentials are hardcoded
- Runtime configuration is environment-driven
- `.env` is ignored by Git
- `data/`, `runs/`, `mlruns/`, and local artifacts are excluded from version control
- Docker build context is trimmed with [`.dockerignore`](/Users/joshu/aerotrack/.dockerignore)
- Docker services include healthchecks for both the API and MLflow

## Deployment notes

For deployment-oriented guidance, see [docs/deploy.md](/Users/joshu/aerotrack/docs/deploy.md).

Additional deployment helpers:

- production-oriented env template: [.env.production.example](/Users/joshu/aerotrack/.env.production.example)
- saved sample API responses: [examples/detect_response.json](/Users/joshu/aerotrack/examples/detect_response.json), [examples/track_response.json](/Users/joshu/aerotrack/examples/track_response.json)
- saved demo commands: [examples/demo_commands.md](/Users/joshu/aerotrack/examples/demo_commands.md)

## Supporting files

- Starter EDA notebook: [notebooks/01_eda.ipynb](/Users/joshu/aerotrack/notebooks/01_eda.ipynb)
- Dataset instructions: [data/README.md](/Users/joshu/aerotrack/data/README.md)
- Training entrypoint: [src/train.py](/Users/joshu/aerotrack/src/train.py)
- Tracking pipeline: [src/track.py](/Users/joshu/aerotrack/src/track.py)
- FastAPI application: [api/main.py](/Users/joshu/aerotrack/api/main.py)
- Demo guide: [docs/demo.md](/Users/joshu/aerotrack/docs/demo.md)
- Deployment guide: [docs/deploy.md](/Users/joshu/aerotrack/docs/deploy.md)
- Operator runbook: [docs/runbook.md](/Users/joshu/aerotrack/docs/runbook.md)
- Smoke-test clip helper: [scripts/make_smoke_clip.py](/Users/joshu/aerotrack/scripts/make_smoke_clip.py)
