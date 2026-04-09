# Runbook

This runbook collects the most common commands and troubleshooting steps for `aerotrack`.

## Core commands

Start the stack:

```bash
docker-compose up --build
```

Stop the stack:

```bash
docker-compose down
```

Check service status:

```bash
docker-compose ps
```

Tail logs:

```bash
docker-compose logs -f
```

Health check:

```bash
curl http://localhost:8000/health
```

Metadata check:

```bash
curl http://localhost:8000/metadata
```

## Common demo commands

Single-frame detection:

```bash
curl -X POST "http://localhost:8000/detect" \
  -H "accept: application/json" \
  -F "file=@/absolute/path/to/frame.jpg"
```

Clip-level tracking:

```bash
curl -X POST "http://localhost:8000/track" \
  -H "accept: application/json" \
  -F "file=@/absolute/path/to/clip.mp4"
```

Generate a smoke-test clip:

```bash
python scripts/make_smoke_clip.py \
  --image data/raw/VisDrone2019-DET-val/images/0000271_01401_d_0000380.jpg \
  --output outputs/smoke.mp4
```

Generate the smoke-test clip from the API container:

```bash
docker-compose exec api python scripts/make_smoke_clip.py \
  --image data/raw/VisDrone2019-DET-val/images/0000271_01401_d_0000380.jpg \
  --output outputs/smoke.mp4
```

## Training commands

Local validation run inside Docker:

```bash
docker-compose exec api python -m src.train \
  --data data/visdrone/VisDrone.yaml \
  --epochs 1 \
  --imgsz 640 \
  --batch 2 \
  --mlflow-tracking-uri http://mlflow:5000
```

Higher-cost run:

```bash
docker-compose exec api python -m src.train \
  --data data/visdrone/VisDrone.yaml \
  --epochs 50 \
  --imgsz 1024 \
  --batch 8 \
  --mlflow-tracking-uri http://mlflow:5000
```

## Troubleshooting

### Docker build is huge or slow

- Confirm [`.dockerignore`](/Users/joshu/aerotrack/.dockerignore) exists
- Make sure `data/` is not being sent into the image build context

### MLflow does not start

- Check whether the host-side port is free
- Confirm `MLFLOW_BACKEND_STORE_URI` uses an absolute SQLite path like `sqlite:////mlflow/mlflow.db`

### API starts but `/detect` is slow on first request

- That is expected if the base YOLO weights need to download on first use
- For demos, preload the weights or point `AEROTRACK_MODEL_PATH` to a local model file

### Training dies with exit code 137

- That usually indicates the process was killed under memory pressure
- Reduce `--imgsz` and `--batch`
- Prefer GPU-backed or higher-memory machines for the full default training profile

### Training cannot find the dataset in Docker

- The runtime training code rewrites the dataset YAML path to the local/container path when needed
- Confirm `data/visdrone/VisDrone.yaml` exists and the images / labels directories are populated

