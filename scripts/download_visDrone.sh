#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${ROOT_DIR}/data"
RAW_DIR="${DATA_DIR}/raw"
YOLO_DIR="${DATA_DIR}/visdrone"
TMP_DIR="${DATA_DIR}/tmp"

mkdir -p "${RAW_DIR}" "${YOLO_DIR}" "${TMP_DIR}"

download_file() {
  local url="$1"
  local output="$2"

  if [[ -f "${output}" ]]; then
    echo "Resuming or validating existing archive: ${output}"
  fi

  echo "Downloading ${url}"
  curl -L --fail --retry 3 -C - "${url}" -o "${output}"
}

extract_file() {
  local archive="$1"
  local target="$2"

  if [[ -d "${target}" ]]; then
    echo "Skipping existing extract: ${target}"
    return
  fi

  echo "Extracting ${archive}"
  unzip -q "${archive}" -d "${RAW_DIR}"
}

ensure_split() {
  local url="$1"
  local archive="$2"
  local target="$3"

  if [[ -d "${target}" ]]; then
    echo "Skipping download and extract for existing split: ${target}"
    return
  fi

  download_file "${url}" "${archive}"
  extract_file "${archive}" "${target}"
}

ensure_split \
  "https://github.com/ultralytics/yolov5/releases/download/v1.0/VisDrone2019-DET-train.zip" \
  "${TMP_DIR}/VisDrone2019-DET-train.zip" \
  "${RAW_DIR}/VisDrone2019-DET-train"
ensure_split \
  "https://github.com/ultralytics/yolov5/releases/download/v1.0/VisDrone2019-DET-val.zip" \
  "${TMP_DIR}/VisDrone2019-DET-val.zip" \
  "${RAW_DIR}/VisDrone2019-DET-val"
ensure_split \
  "https://github.com/ultralytics/yolov5/releases/download/v1.0/VisDrone2019-DET-test-dev.zip" \
  "${TMP_DIR}/VisDrone2019-DET-test-dev.zip" \
  "${RAW_DIR}/VisDrone2019-DET-test-dev"

ROOT_DIR_ENV="${ROOT_DIR}" python3 - <<'PY'
import os
import struct
import shutil
from pathlib import Path

ROOT_DIR = Path(os.environ["ROOT_DIR_ENV"])
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
YOLO_DIR = DATA_DIR / "visdrone"

CLASS_NAMES = [
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


def get_image_size(image_path: Path) -> tuple[int, int]:
    with image_path.open("rb") as handle:
        signature = handle.read(26)

    if signature.startswith(b"\211PNG\r\n\032\n"):
        width, height = struct.unpack(">II", signature[16:24])
        return width, height

    if signature[:2] == b"\xff\xd8":
        with image_path.open("rb") as handle:
            handle.read(2)
            while True:
                marker_start = handle.read(1)
                if marker_start != b"\xff":
                    raise ValueError(f"Invalid JPEG marker in {image_path}")

                marker = handle.read(1)
                while marker == b"\xff":
                    marker = handle.read(1)

                if marker in {b"\xc0", b"\xc1", b"\xc2", b"\xc3", b"\xc5", b"\xc6", b"\xc7", b"\xc9", b"\xca", b"\xcb", b"\xcd", b"\xce", b"\xcf"}:
                    segment_length = struct.unpack(">H", handle.read(2))[0]
                    precision = handle.read(1)
                    height, width = struct.unpack(">HH", handle.read(4))
                    return width, height

                if marker in {b"\xd8", b"\xd9"}:
                    continue

                segment_length = struct.unpack(">H", handle.read(2))[0]
                handle.seek(segment_length - 2, 1)

    raise ValueError(f"Unsupported image format: {image_path}")


def ensure_empty_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


for split in ("train", "val", "test"):
    ensure_empty_dir(YOLO_DIR / "images" / split)
for split in ("train", "val"):
    ensure_empty_dir(YOLO_DIR / "labels" / split)

split_map = {
    "train": RAW_DIR / "VisDrone2019-DET-train",
    "val": RAW_DIR / "VisDrone2019-DET-val",
    "test": RAW_DIR / "VisDrone2019-DET-test-dev",
}

for split, source_dir in split_map.items():
    source_images = source_dir / "images"
    target_images = YOLO_DIR / "images" / split
    for image_path in sorted(source_images.glob("*")):
        if image_path.is_file():
            shutil.copy2(image_path, target_images / image_path.name)

for split in ("train", "val"):
    source_dir = split_map[split]
    annotations_dir = source_dir / "annotations"
    image_dir = source_dir / "images"
    target_dir = YOLO_DIR / "labels" / split

    for annotation_path in sorted(annotations_dir.glob("*.txt")):
        image_path = image_dir / f"{annotation_path.stem}.jpg"
        if not image_path.exists():
            image_path = image_dir / f"{annotation_path.stem}.png"
        if not image_path.exists():
            continue

        try:
            width, height = get_image_size(image_path)
        except ValueError:
            continue

        yolo_lines = []
        for line in annotation_path.read_text().splitlines():
            if not line.strip():
                continue
            parts = [part.strip() for part in line.split(",")]
            while parts and parts[-1] == "":
                parts.pop()
            if len(parts) < 8:
                continue

            x, y, w, h, score, category, truncation, occlusion = map(int, parts[:8])
            if category == 0 or score == 0:
                continue

            x_center = (x + w / 2.0) / width
            y_center = (y + h / 2.0) / height
            norm_w = w / width
            norm_h = h / height
            class_id = category - 1
            yolo_lines.append(
                f"{class_id} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}"
            )

        (target_dir / annotation_path.name).write_text("\n".join(yolo_lines))

dataset_yaml = f"""path: {YOLO_DIR}
train: images/train
val: images/val
test: images/test
names:
"""
for idx, name in enumerate(CLASS_NAMES):
    dataset_yaml += f"  {idx}: {name}\n"

(YOLO_DIR / "VisDrone.yaml").write_text(dataset_yaml)
print(f"Prepared YOLO dataset at {YOLO_DIR}")
PY

echo "VisDrone download and conversion complete."
