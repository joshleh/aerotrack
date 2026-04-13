# Windows GPU Setup

This machine has an `RTX 4070 Ti`, which is a good target for the stronger AeroTrack training run. The important caveat is that the visible system Python on this PC is `3.14`, while this repo pins `torch==2.4.1` and `torchvision==0.19.1`. For the cleanest install path, use a separate Python `3.11` virtual environment.

## PowerShell setup

Install Python `3.11` first if `py -3.11` is not available yet.

```powershell
winget install -e --id Python.Python.3.11
```

Create and activate the project environment from the repo root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install the CUDA-enabled PyTorch stack first, then install the rest of the repo requirements:

```powershell
pip install torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
```

Verify that PyTorch can see the GPU:

```powershell
python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no-gpu')"
```

## Dataset prep

Use the native PowerShell helper from the repo root:

```powershell
.\scripts\download_visDrone.ps1
```

That downloads the VisDrone archives, extracts them under `data/raw/`, converts the annotations into YOLO format, and generates `data/visdrone/VisDrone.yaml`.

## Optional MLflow

If you want local experiment tracking, start MLflow in a separate PowerShell window from the repo root:

```powershell
.\.venv\Scripts\Activate.ps1
mlflow server --backend-store-uri sqlite:///mlflow/mlflow.db --default-artifact-root .\mlflow\artifacts --host 127.0.0.1 --port 5001
```

Then open [http://127.0.0.1:5001](http://127.0.0.1:5001).

## Recommended first GPU training command

Run this from the repo root in the activated virtual environment:

```powershell
$env:MPLCONFIGDIR = "$PWD\.venv\var\mplconfig"
$env:YOLO_CONFIG_DIR = "$PWD\.venv\var\ultralytics"
python -m src.train --model models/yolov8m.pt --data data/visdrone/VisDrone.yaml --epochs 50 --imgsz 1024 --batch 4 --name aerotrack-4070ti --mlflow-tracking-uri file:./mlruns
```

Why `batch 4` instead of `8`:

- the handoff suggested `8`, but this exact machine already has some VRAM in use before training starts
- `yolov8m` at `imgsz 1024` on a 12 GB card can be tight, especially on Windows WDDM
- `batch 4` is a safer first run, and you can raise it after you confirm memory headroom

That command logs MLflow artifacts into the local `mlruns/` directory without needing a separate tracking server.

If the first run is stable and VRAM usage stays comfortable, try `--batch 6` on the next run. If you already started the MLflow server on port `5001`, use:

```powershell
$env:MPLCONFIGDIR = "$PWD\.venv\var\mplconfig"
$env:YOLO_CONFIG_DIR = "$PWD\.venv\var\ultralytics"
python -m src.train --model models/yolov8m.pt --data data/visdrone/VisDrone.yaml --epochs 50 --imgsz 1024 --batch 4 --name aerotrack-4070ti --mlflow-tracking-uri http://127.0.0.1:5001
```

## Practical tip

Before launching the longer training run, it is worth closing GPU-heavy desktop apps such as local LLM runtimes, animated wallpaper software, and broadcast or overlay tools so the training job has more stable VRAM headroom.
