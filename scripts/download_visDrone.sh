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
    echo "Skipping existing archive: ${output}"
    return
  fi

  echo "Downloading ${url}"
  curl -L --fail --retry 3 "${url}" -o "${output}"
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

download_file "https://github.com/VisDrone/VisDrone-Dataset/releases/download/v1.0/VisDrone2019-DET-train.zip" "${TMP_DIR}/VisDrone2019-DET-train.zip"
download_file "https://github.com/VisDrone/VisDrone-Dataset/releases/download/v1.0/VisDrone2019-DET-val.zip" "${TMP_DIR}/VisDrone2019-DET-val.zip"
download_file "https://github.com/VisDrone/VisDrone-Dataset/releases/download/v1.0/VisDrone2019-DET-test-dev.zip" "${TMP_DIR}/VisDrone2019-DET-test-dev.zip"

extract_file "${TMP_DIR}/VisDrone2019-DET-train.zip" "${RAW_DIR}/VisDrone2019-DET-train"
extract_file "${TMP_DIR}/VisDrone2019-DET-val.zip" "${RAW_DIR}/VisDrone2019-DET-val"
extract_file "${TMP_DIR}/VisDrone2019-DET-test-dev.zip" "${RAW_DIR}/VisDrone2019-DET-test-dev"

ROOT_DIR_ENV="${ROOT_DIR}" python3 - <<'PY'
import os
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

        import cv2

        image = cv2.imread(str(image_path))
        if image is None:
            continue
        height, width = image.shape[:2]

        yolo_lines = []
        for line in annotation_path.read_text().splitlines():
            if not line.strip():
                continue
            x, y, w, h, score, category, truncation, occlusion = map(int, line.split(","))
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

