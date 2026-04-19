# GPU Run Handoff

This repo now includes the stronger Windows GPU checkpoint from the RTX 4070 Ti machine:

- checkpoint: `models/aerotrack-detector-demo-v2.pt`
- source run: `runs/train/aerotrack-4070ti-strong-v2`
- base model: `models/yolov8m.pt`
- dataset: `data/visdrone/VisDrone.yaml`

## Training config

- epochs: `50`
- image size: `1024`
- batch size: `4`
- optimizer: `AdamW`
- learning rate: `0.001`
- seed: `0`
- deterministic: `True`

## Final validation

- mAP50: `0.549`
- mAP50-95: `0.349`

Per-class validation from the saved run:

- pedestrian: `mAP50 0.623`, `mAP50-95 0.323`
- people: `mAP50 0.500`, `mAP50-95 0.224`
- bicycle: `mAP50 0.334`, `mAP50-95 0.166`
- car: `mAP50 0.879`, `mAP50-95 0.660`
- van: `mAP50 0.579`, `mAP50-95 0.432`
- truck: `mAP50 0.518`, `mAP50-95 0.366`
- tricycle: `mAP50 0.455`, `mAP50-95 0.277`
- awning-tricycle: `mAP50 0.250`, `mAP50-95 0.170`
- bus: `mAP50 0.718`, `mAP50-95 0.548`
- motor: `mAP50 0.629`, `mAP50-95 0.323`

## What To Pull On The MacBook

Pull these committed changes:

- Windows dataset prep support in `scripts/download_visDrone.ps1` and `scripts/prepare_visdrone.py`
- the shared VisDrone shell-script refactor in `scripts/download_visDrone.sh`
- the Windows training notes in `docs/windows_gpu_setup.md`
- the training fixes in `src/train.py`
- this handoff note
- the saved checkpoint `models/aerotrack-detector-demo-v2.pt`

Do not commit or sync these generated local artifacts:

- `.venv/`
- `data/visdrone/`
- `data/raw/`
- `mlruns/`
- `runs/`
- `models/yolov8m.pt`
- `yolo11n.pt`

## MacBook Next Step

To test the stronger checkpoint on the MacBook without changing the default demo checkpoint, point inference at:

```dotenv
AEROTRACK_MODEL_PATH=models/aerotrack-detector-demo-v2.pt
```

That lets the MacBook compare the stronger GPU-trained model against the existing validated checkpoint before promoting it as the new default.
