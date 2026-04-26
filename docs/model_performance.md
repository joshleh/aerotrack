# Model Performance

The AeroTrack row is seeded from the saved RTX 4070 Ti validation run documented in
`docs/gpu_training_summary.md`. Regenerate this file with:

```bash
python scripts/evaluate_mAP.py
```

| Model | Role | mAP@0.5 | mAP@0.5:0.95 | Lowest AP@0.5 classes |
| --- | --- | ---: | ---: | --- |
| AeroTrack YOLOv8m fine-tune | VisDrone fine-tuned detector | 0.549 | 0.349 | awning-tricycle (0.250), bicycle (0.334), tricycle (0.455) |
| Stock YOLOv8n | Zero-shot COCO baseline | pending | pending | Run `scripts/evaluate_mAP.py` to generate |

## Per-Class AP@0.5

| Model | pedestrian | people | bicycle | car | van | truck | tricycle | awning-tricycle | bus | motor |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| AeroTrack YOLOv8m fine-tune | 0.623 | 0.500 | 0.334 | 0.879 | 0.579 | 0.518 | 0.455 | 0.250 | 0.718 | 0.629 |
| Stock YOLOv8n | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

## Per-Class AP@0.5:0.95

| Model | pedestrian | people | bicycle | car | van | truck | tricycle | awning-tricycle | bus | motor |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| AeroTrack YOLOv8m fine-tune | 0.323 | 0.224 | 0.166 | 0.660 | 0.432 | 0.366 | 0.277 | 0.170 | 0.548 | 0.323 |
| Stock YOLOv8n | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

## Interpretation Notes

- VisDrone is difficult because objects are small, dense, frequently occluded, and viewed from an aerial perspective.
- Cars and buses are the strongest classes because they have larger, more consistent visual footprints from above.
- Bicycle, tricycle, and awning-tricycle are weaker because they are small, visually similar, and often partially occluded in dense scenes.
- The stock `yolov8n.pt` row is a zero-shot baseline. It is useful to show why VisDrone fine-tuning matters, but its COCO class taxonomy does not exactly match VisDrone, so regenerate and interpret it carefully before presenting publicly.
