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

PYTHON_BIN="${PYTHON_BIN:-python3}"
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/prepare_visdrone.py" --root "${ROOT_DIR}"

echo "VisDrone download and conversion complete."
