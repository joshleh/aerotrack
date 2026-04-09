from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from urllib.request import urlopen


def _resolve_target_path(model_path: str) -> Path:
    candidate = Path(model_path)
    return candidate


def _download_model(model_url: str, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(model_url) as response, target_path.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def main() -> int:
    output_dir = os.getenv("AEROTRACK_OUTPUT_DIR", "/app/outputs")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    model_path = os.getenv("AEROTRACK_MODEL_PATH", "yolov8m.pt")
    model_url = os.getenv("AEROTRACK_MODEL_URL", "").strip()
    target_path = _resolve_target_path(model_path)

    if target_path.exists():
        print(f"[bootstrap] Model already present at {target_path}")
        return 0

    if model_url:
        print(f"[bootstrap] Downloading model from {model_url} to {target_path}")
        _download_model(model_url, target_path)
        print("[bootstrap] Model download complete")
        return 0

    if Path(model_path).is_absolute() or len(Path(model_path).parts) > 1:
        print(
            "[bootstrap] Model path does not exist and no AEROTRACK_MODEL_URL was provided: "
            f"{model_path}",
            file=sys.stderr,
        )
        return 1

    print(
        "[bootstrap] No bundled model found. The API will rely on Ultralytics to fetch "
        f"{model_path} on first inference if needed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
