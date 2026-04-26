"""Export the AeroTrack YOLOv8 checkpoint to ONNX and verify parity.

Usage:
    python scripts/export_onnx.py
    python scripts/export_onnx.py --sample-image data/visdrone/images/val/example.jpg

Expected output:
    - models/aerotrack-detector.onnx
    - A confirmation line showing the PyTorch-vs-ONNX Runtime max coordinate
      difference is below one pixel on a VisDrone validation frame.
"""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "aerotrack-detector-demo-v2.pt"
DEFAULT_ONNX_PATH = PROJECT_ROOT / "models" / "aerotrack-detector.onnx"
DEFAULT_VAL_IMAGE_DIR = PROJECT_ROOT / "data" / "visdrone" / "images" / "val"
DEFAULT_SAMPLE_IMAGE = PROJECT_ROOT / "examples" / "sample_media" / "sample_frame.jpg"

IMAGE_SIZE = 640
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
MAX_COORDINATE_DIFF_PX = 1.0
SAMPLE_SCAN_LIMIT = 50
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png")
CPU_DEVICE = "cpu"


@dataclass(frozen=True)
class Detection:
    class_id: int
    confidence: float
    xyxy: tuple[float, float, float, float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export AeroTrack YOLOv8 weights to ONNX.")
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH, type=Path, help="PyTorch checkpoint path.")
    parser.add_argument("--output", default=DEFAULT_ONNX_PATH, type=Path, help="ONNX output path.")
    parser.add_argument("--val-image-dir", default=DEFAULT_VAL_IMAGE_DIR, type=Path, help="Validation image directory.")
    parser.add_argument("--sample-image", default=None, type=Path, help="Optional image to use for ONNX parity checks.")
    parser.add_argument("--imgsz", default=IMAGE_SIZE, type=int, help="Export and inference image size.")
    parser.add_argument("--conf", default=CONFIDENCE_THRESHOLD, type=float, help="Prediction confidence threshold.")
    parser.add_argument("--iou", default=IOU_THRESHOLD, type=float, help="Prediction IoU threshold.")
    return parser.parse_args()


def candidate_images(sample_image: Path | None, val_image_dir: Path) -> list[Path]:
    if sample_image is not None:
        return [sample_image]

    if val_image_dir.exists():
        images = [
            image_path
            for image_path in sorted(val_image_dir.iterdir())
            if image_path.suffix.lower() in IMAGE_SUFFIXES
        ]
        if images:
            return images[:SAMPLE_SCAN_LIMIT]

    return [DEFAULT_SAMPLE_IMAGE]


def read_image(image_path: Path) -> object:
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Unable to read image: {image_path}")
    return image


def extract_detections(
    model: YOLO,
    image: object,
    *,
    image_size: int,
    confidence_threshold: float,
    iou_threshold: float,
) -> list[Detection]:
    result = model.predict(
        image,
        imgsz=image_size,
        conf=confidence_threshold,
        iou=iou_threshold,
        device=CPU_DEVICE,
        verbose=False,
    )[0]
    if result.boxes is None:
        return []

    boxes = result.boxes.xyxy.cpu().numpy()
    class_ids = result.boxes.cls.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    detections = [
        Detection(
            class_id=int(class_id),
            confidence=float(confidence),
            xyxy=tuple(float(coordinate) for coordinate in box),
        )
        for box, class_id, confidence in zip(boxes, class_ids, confidences)
    ]
    return sorted(detections, key=lambda detection: detection.confidence, reverse=True)


def select_verification_frame(
    model: YOLO,
    image_paths: Sequence[Path],
    *,
    image_size: int,
    confidence_threshold: float,
    iou_threshold: float,
) -> tuple[Path, object, list[Detection]]:
    for image_path in image_paths:
        image = read_image(image_path)
        detections = extract_detections(
            model,
            image,
            image_size=image_size,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
        )
        if detections:
            return image_path, image, detections

    raise RuntimeError(
        "Could not find a verification image with detections. "
        "Pass --sample-image with a representative VisDrone frame."
    )


def coordinate_difference(left: Detection, right: Detection) -> float:
    return max(abs(left_coord - right_coord) for left_coord, right_coord in zip(left.xyxy, right.xyxy))


def max_coordinate_difference(
    pytorch_detections: Sequence[Detection],
    onnx_detections: Sequence[Detection],
) -> float:
    if len(pytorch_detections) != len(onnx_detections):
        raise AssertionError(
            "PyTorch and ONNX produced different detection counts: "
            f"{len(pytorch_detections)} vs {len(onnx_detections)}"
        )

    unmatched_onnx_indices = set(range(len(onnx_detections)))
    differences: list[float] = []

    for pytorch_detection in pytorch_detections:
        same_class_candidates = [
            (index, coordinate_difference(pytorch_detection, onnx_detections[index]))
            for index in unmatched_onnx_indices
            if onnx_detections[index].class_id == pytorch_detection.class_id
        ]
        if not same_class_candidates:
            raise AssertionError(f"No ONNX detection matched class {pytorch_detection.class_id}")

        match_index, match_difference = min(same_class_candidates, key=lambda item: item[1])
        unmatched_onnx_indices.remove(match_index)
        differences.append(match_difference)

    return max(differences) if differences else 0.0


def export_to_onnx(model: YOLO, output_path: Path, image_size: int) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # INTERVIEW CRITICAL: ONNX is the bridge format that lets the same trained
    # network move from PyTorch into runtime-specific optimizers such as
    # TensorRT or OpenVINO without retraining the detector.
    exported_path = Path(model.export(format="onnx", dynamic=False, simplify=True, imgsz=image_size))

    if exported_path.resolve() != output_path.resolve():
        shutil.copy2(exported_path, output_path)
    return output_path


def main() -> None:
    args = parse_args()
    model_path = args.model.resolve()
    onnx_path = args.output.resolve()

    if not model_path.exists():
        raise FileNotFoundError(f"Missing PyTorch checkpoint: {model_path}")

    pytorch_model = YOLO(str(model_path))
    verification_image_path, verification_image, pytorch_detections = select_verification_frame(
        pytorch_model,
        candidate_images(args.sample_image, args.val_image_dir),
        image_size=args.imgsz,
        confidence_threshold=args.conf,
        iou_threshold=args.iou,
    )

    exported_path = export_to_onnx(pytorch_model, onnx_path, args.imgsz)

    onnx_model = YOLO(str(exported_path))
    onnx_detections = extract_detections(
        onnx_model,
        verification_image,
        image_size=args.imgsz,
        confidence_threshold=args.conf,
        iou_threshold=args.iou,
    )
    max_diff = max_coordinate_difference(pytorch_detections, onnx_detections)

    if max_diff >= MAX_COORDINATE_DIFF_PX:
        raise AssertionError(
            f"ONNX coordinate parity failed: max diff {max_diff:.3f}px "
            f">= {MAX_COORDINATE_DIFF_PX:.3f}px"
        )

    print(f"Exported ONNX model: {exported_path}")
    print(
        "Verified ONNX Runtime parity against PyTorch on "
        f"{verification_image_path}: {len(pytorch_detections)} detections, "
        f"max coordinate diff {max_diff:.3f}px < {MAX_COORDINATE_DIFF_PX:.1f}px."
    )


if __name__ == "__main__":
    main()
