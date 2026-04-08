# aerotrack

Production-style MLOps repository for multi-object detection and tracking on aerial drone footage. The stack is designed around Anduril-relevant perception needs: airborne sensing, dense urban scenes, persistent multi-object tracks, reproducible training, and containerized deployment for real-time inference workflows.

## What is included

- YOLOv8m fine-tuning on VisDrone2019-DET with MLflow experiment tracking and model registration
- ByteTrack-based multi-object tracking over drone video
- FastAPI inference service for single-image detection and uploaded-video tracking
- Docker and Docker Compose services for the API and an MLflow tracking server
- Dataset download, conversion, and starter EDA notebook for VisDrone

## Architecture

```text
                    +---------------------------+
                    |   VisDrone2019-DET Data   |
                    | raw zips -> YOLO format   |
                    +-------------+-------------+
                                  |
                                  v
                     +------------+------------+
                     |        src/train.py     |
                     | YOLOv8m fine-tuning     |
                     | + MLflow metrics/logs   |
                     +------------+------------+
                                  |
                                  v
                     +------------+------------+
                     |       MLflow Server     |
                     | runs, metrics, models   |
                     +------------+------------+
                                  |
               +------------------+------------------+
               |                                     |
               v                                     v
     +---------+----------+               +----------+---------+
     |   src/predict.py   |               |    src/track.py    |
     | frame detections   |               | YOLO + ByteTrack   |
     +---------+----------+               +----------+---------+
               |                                     |
               +------------------+------------------+
                                  |
                                  v
                     +------------+------------+
                     |        FastAPI API      |
                     | /detect and /track      |
                     +-------------------------+
```

## Repository layout

```text
aerotrack/
├── api/
├── data/
├── mlflow/
├── notebooks/
├── scripts/
├── src/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository and enter it.

```bash
git clone <your-repo-url>
cd aerotrack
```

2. Create your environment file.

```bash
cp .env.example .env
```

Recommended `.env` values for local Docker use:

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

4. Start the inference API and MLflow tracking server.

```bash
docker-compose up --build
```

## Training

Run YOLOv8m fine-tuning and log everything to MLflow:

```bash
python -m src.train \
  --data data/visdrone/VisDrone.yaml \
  --epochs 50 \
  --imgsz 1024 \
  --batch 8 \
  --lr 0.001 \
  --mlflow-tracking-uri "$MLFLOW_TRACKING_URI"
```

The training script logs:

- hyperparameters
- per-epoch loss curves
- `mAP50`
- `mAP50-95`
- Ultralytics plots and result CSVs
- final model artifact

The best model is registered in the MLflow Model Registry as `aerotrack-detector` by default.

Model Registry support depends on the MLflow backend store. Use a database-backed backend store such as SQLite or Postgres for registry features. The provided local setup uses SQLite via `MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow/mlflow.db`.

## Inference API

### `POST /detect`

Single-frame detection with multipart image upload:

```bash
curl -X POST "http://localhost:8000/detect" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/absolute/path/to/frame.jpg"
```

Response shape:

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

Video tracking with multipart upload:

```bash
curl -X POST "http://localhost:8000/track" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/absolute/path/to/clip.mp4"
```

Response shape:

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

## MLflow

After `docker-compose up`, open [http://localhost:5001](http://localhost:5001) to inspect experiments, compare runs, and browse the registered `aerotrack-detector` model versions.

## Notes

- No credentials, paths, or tracking URIs are hardcoded in application code; runtime configuration is sourced from environment variables.
- `data/`, `runs/`, `mlruns/`, and `.env` are ignored by Git.
- The starter notebook lives at [notebooks/01_eda.ipynb](/Users/joshu/aerotrack/notebooks/01_eda.ipynb).
