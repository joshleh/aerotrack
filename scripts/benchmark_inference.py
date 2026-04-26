"""Benchmark AeroTrack PyTorch and ONNX Runtime inference backends.

Usage:
    python scripts/export_onnx.py
    python scripts/benchmark_inference.py

Expected output:
    - Console latency/FPS results for available backends.
    - docs/inference_benchmarks.md containing the same results as a Markdown
      table suitable for the README.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import cv2
import onnxruntime as ort
import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PYTORCH_MODEL_PATH = PROJECT_ROOT / "models" / "aerotrack-detector-demo-v2.pt"
DEFAULT_ONNX_MODEL_PATH = PROJECT_ROOT / "models" / "aerotrack-detector.onnx"
DEFAULT_VAL_IMAGE_DIR = PROJECT_ROOT / "data" / "visdrone" / "images" / "val"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "docs" / "inference_benchmarks.md"

IMAGE_SIZE = 640
WARMUP_ITERATIONS = 10
BENCHMARK_ITERATIONS = 100
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
CUDA_DEVICE_INDEX = 0
MILLISECONDS_PER_SECOND = 1_000.0
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png")


@dataclass(frozen=True)
class BenchmarkBackend:
    name: str
    device_label: str
    model_path: Path
    device_argument: str | int
    synchronize: Callable[[], None]


@dataclass(frozen=True)
class BenchmarkResult:
    backend: str
    device: str
    mean_latency_ms: float
    throughput_fps: float
    warmup_iterations: int
    benchmark_iterations: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark AeroTrack inference latency and throughput.")
    parser.add_argument("--pytorch-model", default=DEFAULT_PYTORCH_MODEL_PATH, type=Path, help="PyTorch checkpoint.")
    parser.add_argument("--onnx-model", default=DEFAULT_ONNX_MODEL_PATH, type=Path, help="ONNX checkpoint.")
    parser.add_argument("--val-image-dir", default=DEFAULT_VAL_IMAGE_DIR, type=Path, help="Validation image directory.")
    parser.add_argument("--sample-image", default=None, type=Path, help="Optional benchmark image path.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH, type=Path, help="Markdown output path.")
    parser.add_argument("--imgsz", default=IMAGE_SIZE, type=int, help="Inference image size.")
    parser.add_argument("--warmup", default=WARMUP_ITERATIONS, type=int, help="Warmup iterations per backend.")
    parser.add_argument("--iterations", default=BENCHMARK_ITERATIONS, type=int, help="Measured iterations per backend.")
    parser.add_argument("--conf", default=CONFIDENCE_THRESHOLD, type=float, help="Prediction confidence threshold.")
    parser.add_argument("--iou", default=IOU_THRESHOLD, type=float, help="Prediction IoU threshold.")
    return parser.parse_args()


def no_op_synchronize() -> None:
    return None


def cuda_synchronize() -> None:
    torch.cuda.synchronize(CUDA_DEVICE_INDEX)


def first_available_image(sample_image: Path | None, val_image_dir: Path) -> Path:
    if sample_image is not None:
        return sample_image

    if val_image_dir.exists():
        for image_path in sorted(val_image_dir.iterdir()):
            if image_path.suffix.lower() in IMAGE_SUFFIXES:
                return image_path

    raise FileNotFoundError(
        "No benchmark image found. Pass --sample-image or prepare data/visdrone/images/val."
    )


def load_frame(image_path: Path, image_size: int) -> Any:
    frame = cv2.imread(str(image_path))
    if frame is None:
        raise FileNotFoundError(f"Unable to read benchmark image: {image_path}")
    return cv2.resize(frame, (image_size, image_size), interpolation=cv2.INTER_LINEAR)


def available_backends(pytorch_model_path: Path, onnx_model_path: Path) -> list[BenchmarkBackend]:
    if not pytorch_model_path.exists():
        raise FileNotFoundError(f"Missing PyTorch checkpoint: {pytorch_model_path}")
    if not onnx_model_path.exists():
        raise FileNotFoundError(
            f"Missing ONNX checkpoint: {onnx_model_path}. Run scripts/export_onnx.py first."
        )

    backends = [
        BenchmarkBackend(
            name="PyTorch",
            device_label="CPU",
            model_path=pytorch_model_path,
            device_argument="cpu",
            synchronize=no_op_synchronize,
        ),
    ]

    if torch.cuda.is_available():
        backends.append(
            BenchmarkBackend(
                name="PyTorch",
                device_label=f"CUDA:{CUDA_DEVICE_INDEX}",
                model_path=pytorch_model_path,
                device_argument=CUDA_DEVICE_INDEX,
                synchronize=cuda_synchronize,
            )
        )

    backends.append(
        BenchmarkBackend(
            name="ONNX Runtime",
            device_label="CPU",
            model_path=onnx_model_path,
            device_argument="cpu",
            synchronize=no_op_synchronize,
        )
    )

    if "CUDAExecutionProvider" in ort.get_available_providers():
        backends.append(
            BenchmarkBackend(
                name="ONNX Runtime",
                device_label=f"CUDA:{CUDA_DEVICE_INDEX}",
                model_path=onnx_model_path,
                device_argument=CUDA_DEVICE_INDEX,
                synchronize=no_op_synchronize,
            )
        )

    return backends


def run_prediction(
    model: YOLO,
    frame: Any,
    *,
    image_size: int,
    confidence_threshold: float,
    iou_threshold: float,
    device_argument: str | int,
) -> None:
    model.predict(
        frame,
        imgsz=image_size,
        conf=confidence_threshold,
        iou=iou_threshold,
        device=device_argument,
        verbose=False,
    )


def benchmark_backend(
    backend: BenchmarkBackend,
    frame: Any,
    *,
    image_size: int,
    warmup_iterations: int,
    benchmark_iterations: int,
    confidence_threshold: float,
    iou_threshold: float,
) -> BenchmarkResult:
    model = YOLO(str(backend.model_path))

    for _ in range(warmup_iterations):
        run_prediction(
            model,
            frame,
            image_size=image_size,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
            device_argument=backend.device_argument,
        )
    backend.synchronize()

    latencies_ms: list[float] = []
    for _ in range(benchmark_iterations):
        backend.synchronize()
        start = time.perf_counter()
        run_prediction(
            model,
            frame,
            image_size=image_size,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
            device_argument=backend.device_argument,
        )
        # INTERVIEW CRITICAL: CUDA work is asynchronous, so synchronizing around
        # timed regions keeps GPU latency numbers honest instead of measuring
        # only kernel launch overhead.
        backend.synchronize()
        elapsed_ms = (time.perf_counter() - start) * MILLISECONDS_PER_SECOND
        latencies_ms.append(elapsed_ms)

    mean_latency_ms = sum(latencies_ms) / len(latencies_ms)
    throughput_fps = MILLISECONDS_PER_SECOND / mean_latency_ms
    return BenchmarkResult(
        backend=backend.name,
        device=backend.device_label,
        mean_latency_ms=mean_latency_ms,
        throughput_fps=throughput_fps,
        warmup_iterations=warmup_iterations,
        benchmark_iterations=benchmark_iterations,
    )


def markdown_table(results: list[BenchmarkResult]) -> list[str]:
    lines = [
        "| Backend | Device | Mean latency (ms) | Throughput (FPS) | Warmup | Iterations |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        lines.append(
            "| "
            f"{result.backend} | {result.device} | "
            f"{result.mean_latency_ms:.2f} | {result.throughput_fps:.2f} | "
            f"{result.warmup_iterations} | {result.benchmark_iterations} |"
        )
    return lines


def write_markdown(results: list[BenchmarkResult], output_path: Path, image_path: Path, image_size: int) -> None:
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "# Inference Benchmarks",
        "",
        f"Generated: `{generated_at}`",
        f"Benchmark frame: `{image_path}` resized to `{image_size}x{image_size}`.",
        "",
        *markdown_table(results),
        "",
        "## Notes",
        "",
        "- PyTorch rows measure the Ultralytics checkpoint directly.",
        "- ONNX Runtime rows measure the exported ONNX graph through Ultralytics' ONNX backend.",
        "- Install `onnxruntime-gpu` on a CUDA host to enable the ONNX Runtime GPU row.",
        "- TensorRT benchmarking should be repeated on the actual Jetson or edge GPU target.",
        "",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    image_path = first_available_image(args.sample_image, args.val_image_dir)
    frame = load_frame(image_path, args.imgsz)
    results = [
        benchmark_backend(
            backend,
            frame,
            image_size=args.imgsz,
            warmup_iterations=args.warmup,
            benchmark_iterations=args.iterations,
            confidence_threshold=args.conf,
            iou_threshold=args.iou,
        )
        for backend in available_backends(args.pytorch_model.resolve(), args.onnx_model.resolve())
    ]

    write_markdown(results, args.output.resolve(), image_path.resolve(), args.imgsz)
    print("\n".join(markdown_table(results)))
    print(f"\nSaved benchmark table to {args.output.resolve()}")


if __name__ == "__main__":
    main()
