"""Evaluate AeroTrack and a stock YOLOv8 baseline on VisDrone validation data.

Usage:
    python scripts/evaluate_mAP.py
    python scripts/evaluate_mAP.py --device 0 --batch 16

Expected output:
    - Ultralytics validation metrics for both models.
    - docs/model_performance.md with summary mAP and per-class AP tables.
"""

from __future__ import annotations

import argparse
import math
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_YAML = PROJECT_ROOT / "data" / "visdrone" / "VisDrone.yaml"
DEFAULT_TRAINED_MODEL_PATH = PROJECT_ROOT / "models" / "aerotrack-detector-demo-v2.pt"
DEFAULT_BASELINE_MODEL = "yolov8n.pt"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "docs" / "model_performance.md"
DEFAULT_RUNS_PROJECT = PROJECT_ROOT / "runs" / "val"

IMAGE_SIZE = 640
BATCH_SIZE = 8
DEVICE_AUTO = "auto"
VALIDATION_SPLIT = "val"
METRIC_PRECISION = 3
LOWEST_CLASS_COUNT = 3


@dataclass(frozen=True)
class EvaluationResult:
    display_name: str
    model: str
    role: str
    map50: float
    map50_95: float
    per_class_ap50: dict[str, float | None]
    per_class_ap50_95: dict[str, float | None]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate AeroTrack mAP on VisDrone validation data.")
    parser.add_argument("--data", default=DEFAULT_DATASET_YAML, type=Path, help="VisDrone YOLO dataset YAML.")
    parser.add_argument("--trained-model", default=DEFAULT_TRAINED_MODEL_PATH, type=Path, help="AeroTrack checkpoint.")
    parser.add_argument("--baseline-model", default=DEFAULT_BASELINE_MODEL, help="Stock YOLO baseline checkpoint.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH, type=Path, help="Markdown output path.")
    parser.add_argument("--imgsz", default=IMAGE_SIZE, type=int, help="Validation image size.")
    parser.add_argument("--batch", default=BATCH_SIZE, type=int, help="Validation batch size.")
    parser.add_argument("--device", default=DEVICE_AUTO, help="Ultralytics device argument, or 'auto'.")
    return parser.parse_args()


def resolve_dataset_yaml(dataset_yaml_path: Path) -> Path:
    dataset_path = dataset_yaml_path.resolve()
    if not dataset_path.exists():
        raise FileNotFoundError(f"Missing dataset YAML: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as handle:
        dataset_config = yaml.safe_load(handle)

    configured_root = dataset_config.get("path")
    if configured_root:
        configured_root_path = Path(configured_root)
        train_dir = configured_root_path / str(dataset_config.get("train", "images/train"))
        val_dir = configured_root_path / str(dataset_config.get("val", "images/val"))
        if train_dir.exists() and val_dir.exists():
            return dataset_path

    dataset_config["path"] = str(dataset_path.parent)
    temp_dir = Path(tempfile.mkdtemp(prefix="aerotrack-val-data-"))
    resolved_yaml_path = temp_dir / dataset_path.name
    with resolved_yaml_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(dataset_config, handle, sort_keys=False)
    return resolved_yaml_path


def as_float(value: Any) -> float:
    return float(value.item() if hasattr(value, "item") else value)


def metric_sequence(values: Any) -> list[float]:
    if values is None:
        return []
    if hasattr(values, "tolist"):
        values = values.tolist()
    return [float(value) for value in values]


def load_dataset_class_names(dataset_yaml: Path) -> dict[int, str]:
    with dataset_yaml.open("r", encoding="utf-8") as handle:
        dataset_config = yaml.safe_load(handle)

    names = dataset_config.get("names", {})
    if isinstance(names, dict):
        return {int(index): str(name) for index, name in names.items()}
    if isinstance(names, list):
        return {index: str(name) for index, name in enumerate(names)}
    return {}


def per_class_metrics(
    metrics: Any,
    class_names: dict[int, str],
) -> tuple[dict[str, float | None], dict[str, float | None]]:
    box_metrics = metrics.box
    ap_class_indices = [int(index) for index in metric_sequence(getattr(box_metrics, "ap_class_index", []))]
    ap50_values = metric_sequence(getattr(box_metrics, "ap50", []))
    ap_values = metric_sequence(getattr(box_metrics, "ap", []))

    ap50_by_class = {name: None for _, name in sorted(class_names.items())}
    ap_by_class = {name: None for _, name in sorted(class_names.items())}

    for position, class_index in enumerate(ap_class_indices):
        class_name = class_names.get(class_index, str(class_index))
        if position < len(ap50_values):
            ap50_by_class[class_name] = ap50_values[position]
        if position < len(ap_values):
            ap_by_class[class_name] = ap_values[position]

    return ap50_by_class, ap_by_class


def evaluate_model(
    *,
    display_name: str,
    model_path: str | Path,
    role: str,
    dataset_yaml: Path,
    image_size: int,
    batch_size: int,
    device: str,
    class_names: dict[int, str],
) -> EvaluationResult:
    model = YOLO(str(model_path))
    validation_kwargs: dict[str, Any] = {
        "data": str(dataset_yaml),
        "split": VALIDATION_SPLIT,
        "imgsz": image_size,
        "batch": batch_size,
        "project": str(DEFAULT_RUNS_PROJECT),
        "name": display_name.lower().replace(" ", "-"),
        "plots": False,
        "verbose": False,
    }
    if device != DEVICE_AUTO:
        validation_kwargs["device"] = device

    # INTERVIEW CRITICAL: mAP@0.5 rewards detections above one IoU threshold,
    # while mAP@0.5:0.95 averages stricter localization thresholds and is a
    # better signal for precise perception quality.
    metrics = model.val(**validation_kwargs)
    ap50_by_class, ap_by_class = per_class_metrics(metrics, class_names)
    return EvaluationResult(
        display_name=display_name,
        model=str(model_path),
        role=role,
        map50=as_float(metrics.box.map50),
        map50_95=as_float(metrics.box.map),
        per_class_ap50=ap50_by_class,
        per_class_ap50_95=ap_by_class,
    )


def format_metric(value: float | None) -> str:
    if value is None or math.isnan(value):
        return "n/a"
    return f"{value:.{METRIC_PRECISION}f}"


def lowest_classes(result: EvaluationResult, limit: int) -> str:
    available = [
        (class_name, value)
        for class_name, value in result.per_class_ap50.items()
        if value is not None and not math.isnan(value)
    ]
    lowest = sorted(available, key=lambda item: item[1])[:limit]
    return ", ".join(f"{class_name} ({format_metric(value)})" for class_name, value in lowest)


def per_class_table(
    results: list[EvaluationResult],
    class_names: list[str],
    metric_name: str,
) -> list[str]:
    lines = [
        "| Model | " + " | ".join(class_names) + " |",
        "| --- | " + " | ".join("---:" for _ in class_names) + " |",
    ]
    for result in results:
        metric_values = getattr(result, metric_name)
        values = [format_metric(metric_values.get(class_name)) for class_name in class_names]
        lines.append(f"| {result.display_name} | " + " | ".join(values) + " |")
    return lines


def write_markdown(results: list[EvaluationResult], output_path: Path) -> None:
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    class_names = sorted({class_name for result in results for class_name in result.per_class_ap50})
    summary_lines = [
        "| Model | Role | mAP@0.5 | mAP@0.5:0.95 | Lowest AP@0.5 classes |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for result in results:
        summary_lines.append(
            "| "
            f"{result.display_name} | {result.role} | "
            f"{format_metric(result.map50)} | {format_metric(result.map50_95)} | "
            f"{lowest_classes(result, limit=LOWEST_CLASS_COUNT)} |"
        )

    lines = [
        "# Model Performance",
        "",
        f"Generated: `{generated_at}`",
        "",
        *summary_lines,
        "",
        "## Per-Class AP@0.5",
        "",
        *per_class_table(results, class_names, "per_class_ap50"),
        "",
        "## Per-Class AP@0.5:0.95",
        "",
        *per_class_table(results, class_names, "per_class_ap50_95"),
        "",
        "## Interpretation Notes",
        "",
        "- VisDrone is difficult because objects are small, dense, and viewed from an aerial perspective.",
        "- The stock `yolov8n.pt` row is a zero-shot baseline, not a class-taxonomy-perfect comparison.",
        "- Regenerate this file after changing weights, validation image size, or dataset conversion code.",
        "",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    dataset_yaml = resolve_dataset_yaml(args.data)
    class_names = load_dataset_class_names(dataset_yaml)
    trained_model = args.trained_model.resolve()
    if not trained_model.exists():
        raise FileNotFoundError(f"Missing trained checkpoint: {trained_model}")

    results = [
        evaluate_model(
            display_name="AeroTrack YOLOv8m fine-tune",
            model_path=trained_model,
            role="VisDrone fine-tuned detector",
            dataset_yaml=dataset_yaml,
            image_size=args.imgsz,
            batch_size=args.batch,
            device=args.device,
            class_names=class_names,
        ),
        # INTERVIEW CRITICAL: This is a zero-shot stock COCO model. It is useful
        # as a deployment sanity baseline, but its taxonomy does not exactly
        # match VisDrone, so weak classes should not be over-interpreted.
        evaluate_model(
            display_name="Stock YOLOv8n",
            model_path=args.baseline_model,
            role="Zero-shot COCO baseline",
            dataset_yaml=dataset_yaml,
            image_size=args.imgsz,
            batch_size=args.batch,
            device=args.device,
            class_names=class_names,
        ),
    ]
    write_markdown(results, args.output.resolve())
    print(f"Saved model performance report to {args.output.resolve()}")


if __name__ == "__main__":
    main()
