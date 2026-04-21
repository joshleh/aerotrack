# GPU Training Summary

This document captures the stronger AeroTrack checkpoint produced on the Windows machine with an `RTX 4070 Ti`. It is the higher-quality model included in this repo for local evaluation, project review, and future deployment upgrades.

## Checkpoint

- checkpoint: `models/aerotrack-detector-demo-v2.pt`
- base model: `yolov8m.pt`
- source run: `runs/train/aerotrack-4070ti-strong-v2`
- dataset: `data/visdrone/VisDrone.yaml`

## Training configuration

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

## Recommended local use

To evaluate the stronger checkpoint locally, point inference at:

```dotenv
AEROTRACK_MODEL_PATH=models/aerotrack-detector-demo-v2.pt
```

That gives you the higher-quality model for local demos and review while keeping the free public Render deployment on the lighter `yolov8n.pt` live model.
