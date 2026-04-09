from __future__ import annotations

import os
from pathlib import Path

from fastapi import HTTPException


def get_output_root() -> Path:
    return Path(os.getenv("AEROTRACK_OUTPUT_DIR", "/app/outputs")).resolve()


def artifact_url_for_path(file_path: str | Path) -> str:
    output_root = get_output_root()
    resolved_path = Path(file_path).resolve()

    try:
        relative_path = resolved_path.relative_to(output_root)
    except ValueError as exc:
        raise ValueError(f"Artifact path is outside the configured output directory: {file_path}") from exc

    return f"/artifacts/{relative_path.as_posix()}"


def resolve_artifact_path(artifact_path: str) -> Path:
    output_root = get_output_root()
    resolved_path = (output_root / artifact_path).resolve()

    try:
        resolved_path.relative_to(output_root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Artifact not found.") from exc

    if not resolved_path.exists() or not resolved_path.is_file():
        raise HTTPException(status_code=404, detail="Artifact not found.")

    return resolved_path
