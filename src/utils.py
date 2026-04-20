from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO

VISDRONE_CLASS_NAMES = [
    "pedestrian",
    "people",
    "bicycle",
    "car",
    "van",
    "truck",
    "tricycle",
    "awning-tricycle",
    "bus",
    "motor",
]


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=4)
def _cached_model(model_path: str) -> YOLO:
    return YOLO(model_path)


def load_yolo_model(model_path: str | None = None) -> YOLO:
    resolved_path = model_path or get_env("AEROTRACK_MODEL_PATH")
    return _cached_model(resolved_path)


def get_runtime_thresholds() -> tuple[float, float]:
    confidence = float(get_env("AEROTRACK_CONFIDENCE"))
    iou = float(get_env("AEROTRACK_IOU"))
    return confidence, iou


def get_inference_device() -> str | None:
    return os.getenv("AEROTRACK_DEVICE")


def get_optional_int_env(name: str) -> int | None:
    value = os.getenv(name)
    if value in {None, ""}:
        return None
    return int(value)


def get_inference_imgsz() -> int | None:
    return get_optional_int_env("AEROTRACK_PREDICT_IMGSZ")


def get_track_max_frames() -> int | None:
    return get_optional_int_env("AEROTRACK_TRACK_MAX_FRAMES")


def xyxy_to_xywh(xyxy: list[float]) -> list[float]:
    x1, y1, x2, y2 = xyxy
    return [x1, y1, x2 - x1, y2 - y1]


def color_for_track(track_id: int) -> tuple[int, int, int]:
    palette = (
        (56, 56, 255),
        (151, 157, 255),
        (31, 112, 255),
        (29, 178, 255),
        (49, 210, 207),
        (10, 249, 72),
        (23, 204, 146),
        (134, 219, 61),
        (52, 147, 26),
        (187, 212, 0),
    )
    return palette[track_id % len(palette)]


def encode_image(image: np.ndarray, extension: str = ".jpg") -> bytes:
    ok, buffer = cv2.imencode(extension, image)
    if not ok:
        raise ValueError("Failed to encode image.")
    return buffer.tobytes()


def save_json(payload: Any, output_path: str | Path) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(output_path).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def parse_yolo_result(result: Any) -> list[dict[str, Any]]:
    detections: list[dict[str, Any]] = []
    if result.boxes is None:
        return detections

    names = result.names or {idx: name for idx, name in enumerate(VISDRONE_CLASS_NAMES)}
    for box in result.boxes:
        xyxy = box.xyxy[0].tolist()
        confidence = float(box.conf[0].item())
        class_id = int(box.cls[0].item())
        detections.append(
            {
                "bbox": [round(value, 2) for value in xyxy],
                "class_id": class_id,
                "class_label": names.get(class_id, str(class_id)),
                "confidence": round(confidence, 4),
            }
        )
    return detections


def annotate_frame(
    frame: np.ndarray,
    tracked_objects: list[dict[str, Any]],
) -> np.ndarray:
    annotated = frame.copy()
    for obj in tracked_objects:
        x1, y1, x2, y2 = [int(value) for value in obj["bbox"]]
        track_id = int(obj.get("track_id", -1))
        color = color_for_track(track_id if track_id >= 0 else obj["class_id"])
        label = (
            f'ID {track_id} | {obj["class_label"]} | '
            f'{obj["confidence"]:.2f}'
        )
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            annotated,
            label,
            (x1, max(y1 - 8, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
            cv2.LINE_AA,
        )
    return annotated
